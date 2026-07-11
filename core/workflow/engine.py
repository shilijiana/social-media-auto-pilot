"""工作流引擎 — 编排管线执行与状态管理。"""

import json
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from autosoc.core.database import Database
from autosoc.core.event_bus.bus import EventBus
from autosoc.core.event_bus.events import Event
from autosoc.core.logging import log
from autosoc.core.workflow.models import (
    Pipeline,
    Step,
    StepMode,
    StepStatus,
    StepType,
    WorkflowStatus,
)


class WorkflowEngine:
    """工作流引擎 — 注册管线、创建实例、驱动执行。"""

    def __init__(self, db: Database = None, event_bus: EventBus = None):
        self._db = db or Database.get_instance()
        self._event_bus = event_bus
        self._pipelines: Dict[str, Pipeline] = {}
        self._lock = threading.RLock()
        self._step_handlers: Dict[str, Callable] = {}

    # ── 管线注册 ──────────────────────────────────────

    def register_pipeline(self, pipeline: Pipeline) -> None:
        """注册一条工作流管线定义。"""
        self._pipelines[pipeline.id] = pipeline
        log.info(f"[Workflow] 注册管线: {pipeline.id} ({len(pipeline.steps)} steps)")

    def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        return self._pipelines.get(pipeline_id)

    def register_step_handler(self, module_id: str, handler: Callable) -> None:
        """注册模块处理器，用于根据 module_id 自动调用。"""
        self._step_handlers[module_id] = handler

    # ── 实例管理 ──────────────────────────────────────

    def create_instance(
        self, pipeline_id: str, context: Dict[str, Any] = None
    ) -> int:
        """创建工作流实例，返回 instance_id。

        Args:
            pipeline_id: 管线 ID
            context: 初始上下文数据 (topic_plan_id, input_data 等)

        Returns:
            新创建的 workflow instance ID
        """
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"未知管线: {pipeline_id}")

        step_states = {s.id: StepStatus.PENDING.value for s in pipeline.steps}
        instance_id = self._db.insert(
            "INSERT INTO workflow_instances "
            "(workflow_type, status, current_step, step_states, context_data) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                pipeline_id,
                WorkflowStatus.PENDING.value,
                "",
                json.dumps(step_states),
                json.dumps(context or {}),
            ),
        )
        log.info(f"[Workflow] 创建实例 #{instance_id}: {pipeline_id}")
        return instance_id

    def _update_instance(self, instance_id: int, **kwargs):
        """更新工作流实例字段。"""
        pairs = ", ".join(f"{k}=?" for k in kwargs)
        values = list(kwargs.values())
        values.append(instance_id)
        self._db.execute(
            f"UPDATE workflow_instances SET {pairs}, "
            f"updated_at=datetime('now') WHERE id=?",
            tuple(values),
        )
        self._db.commit()

    def get_instance(self, instance_id: int) -> Optional[dict]:
        row = self._db.fetchone(
            "SELECT * FROM workflow_instances WHERE id=?", (instance_id,)
        )
        if row:
            return dict(row)
        return None

    # ── 执行控制 ──────────────────────────────────────

    def start(self, instance_id: int) -> None:
        """启动工作流实例。"""
        instance = self.get_instance(instance_id)
        if not instance:
            raise ValueError(f"实例不存在: {instance_id}")

        pipeline = self.get_pipeline(instance["workflow_type"])
        if not pipeline:
            raise ValueError(f"管线不存在: {instance['workflow_type']}")

        self._update_instance(
            instance_id,
            status=WorkflowStatus.RUNNING.value,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        entry_steps = pipeline.get_entry_steps()
        for step in entry_steps:
            self._execute_step(instance_id, pipeline, step, {})

    def pause(self, instance_id: int) -> None:
        self._update_instance(instance_id, status=WorkflowStatus.PAUSED.value)
        log.info(f"[Workflow] 暂停实例 #{instance_id}")

    def resume(self, instance_id: int) -> None:
        self._update_instance(instance_id, status=WorkflowStatus.RUNNING.value)
        log.info(f"[Workflow] 恢复实例 #{instance_id}")

    def cancel(self, instance_id: int) -> None:
        self._update_instance(instance_id, status=WorkflowStatus.CANCELLED.value)
        log.info(f"[Workflow] 取消实例 #{instance_id}")

    # ── 步骤执行 ──────────────────────────────────────

    def _execute_step(
        self,
        instance_id: int,
        pipeline: Pipeline,
        step: Step,
        input_data: Dict[str, Any],
    ) -> None:
        """执行单个步骤。"""
        self._update_step_state(instance_id, step.id, StepStatus.RUNNING)
        self._update_instance(instance_id, current_step=step.id)

        log.info(f"[Workflow] #{instance_id} 执行步骤: {step.id} ({step.name})")

        try:
            if step.module_id and step.module_id in self._step_handlers:
                handler = self._step_handlers[step.module_id]
                result = handler({"step": step, "input": input_data})
            elif step.handler:
                result = step.handler({"step": step, "input": input_data})
            else:
                result = {"status": "success", "output": {}}

            self._update_step_state(instance_id, step.id, StepStatus.COMPLETED)
            self._check_completion(instance_id, pipeline)

            # 发布步骤完成事件
            if self._event_bus:
                self._event_bus.publish(
                    Event(
                        event_type=f"step.{step.id}.completed",
                        source_module=step.module_id or "workflow",
                        source_workflow_id=instance_id,
                        payload={"step_id": step.id, "result": result},
                    )
                )

        except Exception as e:
            log.error(f"[Workflow] #{instance_id} 步骤 {step.id} 失败: {e}")
            self._update_step_state(instance_id, step.id, StepStatus.FAILED)
            self._update_instance(instance_id, error_info=json.dumps({"step": step.id, "error": str(e)}))
            # 单个步骤失败不影响整体
            self._check_completion(instance_id, pipeline)

    def _update_step_state(self, instance_id: int, step_id: str, status: StepStatus):
        instance = self.get_instance(instance_id)
        if not instance:
            return
        step_states = json.loads(instance["step_states"])
        step_states[step_id] = status.value
        self._update_instance(instance_id, step_states=json.dumps(step_states))

    def _check_completion(
        self, instance_id: int, pipeline: Pipeline
    ) -> None:
        """检查并执行可执行的下游步骤，或在全部完成后标记完成。"""
        instance = self.get_instance(instance_id)
        if not instance:
            return

        step_states = json.loads(instance["step_states"])
        all_steps = {s.id: s for s in pipeline.steps}

        # 找到所有 pending 状态且依赖已完成的步骤
        for step_id, status_str in step_states.items():
            if status_str != StepStatus.PENDING.value:
                continue
            step = all_steps.get(step_id)
            if not step:
                continue

            deps_met = all(
                step_states.get(dep) == StepStatus.COMPLETED.value
                for dep in step.depends_on
            )
            if deps_met:
                self._execute_step(instance_id, pipeline, step, {})

        # 检查是否全部完成
        completed = all(
            s in (StepStatus.COMPLETED.value, StepStatus.SKIPPED.value)
            for s in step_states.values()
        )
        failed = any(s == StepStatus.FAILED.value for s in step_states.values())

        if completed:
            self._update_instance(
                instance_id,
                status=WorkflowStatus.COMPLETED.value,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            log.info(f"[Workflow] #{instance_id} 完成")
            if pipeline.on_complete:
                pipeline.on_complete(instance_id)
        elif failed and not any(
            s in (StepStatus.RUNNING.value, StepStatus.PENDING.value)
            for s in step_states.values()
        ):
            self._update_instance(instance_id, status=WorkflowStatus.FAILED.value)
            log.warning(f"[Workflow] #{instance_id} 失败")
            if pipeline.on_failure:
                pipeline.on_failure(instance_id)

    def handle_step_callback(
        self, instance_id: int, step_id: str, result: Dict[str, Any]
    ) -> None:
        """处理异步步骤的完成回调（如人工审阅完成）。"""
        pipeline_id = self.get_instance(instance_id).get("workflow_type")
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return
        step = pipeline.get_step(step_id)
        if not step:
            return
        self._execute_step(instance_id, pipeline, step, result)

    def get_p0_pipeline(self) -> Pipeline:
        """创建 P0 标准完整管线定义。"""
        from autosoc.core.workflow.models import Pipeline, Step, StepMode, StepType

        return Pipeline(
            id="p0_full",
            name="P0 完整闭环工作流",
            steps=[
                Step(id="expand_keywords", name="关键词扩展",
                     module_id="M-01", mode=StepMode.AUTO),
                Step(id="gather_materials", name="图文素材采集",
                     module_id="M-02", mode=StepMode.AUTO,
                     depends_on=["expand_keywords"]),
                Step(id="gather_videos", name="视频素材采集",
                     module_id="M-03", mode=StepMode.AUTO,
                     depends_on=["expand_keywords"]),
                Step(id="collect_references", name="参考文案采集",
                     module_id="M-04", mode=StepMode.AUTO,
                     depends_on=["expand_keywords"]),
                Step(id="quality_check", name="去重质检",
                     module_id="M-05", mode=StepMode.AUTO,
                     depends_on=["gather_materials", "gather_videos", "collect_references"]),
                Step(id="match_materials", name="素材匹配",
                     module_id="M-07", mode=StepMode.AUTO,
                     depends_on=["quality_check"]),
                Step(id="generate_text", name="文案生成",
                     module_id="M-08", mode=StepMode.HYBRID,
                     depends_on=["match_materials"]),
                Step(id="generate_cover", name="封面图生成",
                     module_id="M-09", mode=StepMode.AUTO,
                     depends_on=["generate_text"]),
                Step(id="edit_video", name="视频初剪",
                     module_id="M-10", mode=StepMode.AUTO,
                     depends_on=["generate_text"]),
                Step(id="finalize", name="精加工定稿",
                     module_id="M-11", mode=StepMode.AUTO,
                     depends_on=["generate_cover", "edit_video"]),
                Step(id="compliance_check", name="合规自检",
                     module_id="M-12", mode=StepMode.AUTO,
                     depends_on=["finalize"]),
                Step(id="review_content", name="内容审阅",
                     step_type=StepType.REVIEW, mode=StepMode.HYBRID,
                     depends_on=["compliance_check"]),
                Step(id="publish", name="多平台发布",
                     module_id="M-16", mode=StepMode.HYBRID,
                     depends_on=["review_content"]),
                Step(id="monitor", name="发布状态监控",
                     module_id="M-17", mode=StepMode.AUTO,
                     depends_on=["publish"]),
                Step(id="collect_data", name="效果数据采集",
                     module_id="M-18", mode=StepMode.AUTO,
                     depends_on=["monitor"]),
            ],
        )
