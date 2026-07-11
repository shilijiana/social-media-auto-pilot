"""事件总线核心 — 进程内同步/异步发布-订阅实现。"""

import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

from autosoc.core.event_bus.events import Event
from autosoc.core.logging import log

EventHandler = Callable[[Event], None]


class EventBus:
    """进程内事件总线，支持同步和异步两种发布模式。

    使用方式:
        bus = EventBus()
        bus.subscribe("materials.collected", my_handler)
        bus.publish(event)          # 异步
        bus.publish(event, sync=True)  # 同步
    """

    def __init__(
        self,
        max_workers: int = 4,
        async_mode: bool = True,
    ):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="eventbus",
        )
        self._async_mode = async_mode

    # ── 订阅管理 ──────────────────────────────────────

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅指定类型的事件。"""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            log.debug(f"[EventBus] 订阅: {event_type} <- {handler.__name__}")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅。"""
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type] = [
                    h for h in self._handlers[event_type] if h is not handler
                ]

    # ── 发布 ──────────────────────────────────────────

    def publish(self, event: Event, sync: bool = False) -> None:
        """发布事件。

        Args:
            event: 事件对象
            sync: 是否同步阻塞所有订阅者执行完毕
        """
        log.debug(
            f"[EventBus] 发布: {event.event_type} "
            f"(module={event.source_module}, sync={sync})"
        )

        with self._lock:
            handlers = list(self._handlers.get(event.event_type, []))

        if not handlers:
            return

        if sync:
            self._publish_sync(event, handlers)
        else:
            self._publish_async(event, handlers)

    def _publish_sync(self, event: Event, handlers: List[EventHandler]):
        """同步发布：依次调用，异常不影响后续。"""
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                log.error(
                    f"[EventBus] 同步处理器异常: {handler.__name__}: {e}",
                    exc_info=True,
                )

    def _publish_async(self, event: Event, handlers: List[EventHandler]):
        """异步发布：线程池执行。"""
        for handler in handlers:
            self._executor.submit(self._safe_call, handler, event)

    def _safe_call(self, handler: EventHandler, event: Event):
        """安全调用处理器，捕获异常并记录。"""
        try:
            handler(event)
        except Exception as e:
            log.error(
                f"[EventBus] 异步处理器异常: {handler.__name__}: {e}",
                exc_info=True,
            )

    # ── 生命周期 ──────────────────────────────────────

    def shutdown(self, wait: bool = True):
        """关闭事件总线，释放线程池。"""
        self._executor.shutdown(wait=wait)
        log.info("[EventBus] 已关闭")
