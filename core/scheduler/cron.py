"""定时调度器 — 基于 APScheduler 的简化封装，用于定时/延迟任务。"""

from typing import Callable, Optional

from autosoc.core.logging import log


class Scheduler:
    """轻量定时调度器（预留接口，后续集成 APScheduler）。"""

    def __init__(self):
        self._jobs: dict = {}
        self._running = False

    def add_once(self, name: str, func: Callable, run_at: str, args: tuple = None):
        """添加一次性定时任务（run_at: ISO-8601 时间字符串）。"""
        log.info(f"[Scheduler] 添加一次性任务: {name} @ {run_at}")
        self._jobs[name] = {
            "func": func,
            "schedule": run_at,
            "type": "once",
            "args": args or (),
        }

    def add_interval(
        self, name: str, func: Callable, interval_seconds: int, args: tuple = None
    ):
        """添加循环任务。"""
        log.info(f"[Scheduler] 添加循环任务: {name} 每 {interval_seconds}s")
        self._jobs[name] = {
            "func": func,
            "schedule": interval_seconds,
            "type": "interval",
            "args": args or (),
        }

    def remove(self, name: str) -> bool:
        if name in self._jobs:
            del self._jobs[name]
            return True
        return False

    def start(self):
        self._running = True
        log.info("[Scheduler] 启动（当前为 stub，需集成 APScheduler）")

    def stop(self):
        self._running = False
        log.info("[Scheduler] 已停止")
