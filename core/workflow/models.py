"""工作流模型定义 — Pipeline、Step、StepMode、StepType、WorkflowStatus。"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class StepMode(Enum):
    """步骤执行模式，对应三阶段演进策略。"""
    AUTO = "auto"               # 全自动执行
    WAIT_HUMAN = "wait_human"   # 等待人工操作
    HYBRID = "hybrid"           # 自动执行 + 人工可干预


class StepType(Enum):
    """步骤类型。"""
    TASK = "task"               # 普通任务步骤
    REVIEW = "review"           # 审阅步骤（特殊处理）
    DECISION = "decision"       # 条件分支步骤
    PARALLEL = "parallel"       # 并行步骤组


class WorkflowStatus(Enum):
    """工作流实例状态。"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """步骤状态。"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Step:
    """工作流中的一个步骤定义。"""
    id: str
    name: str
    step_type: StepType = StepType.TASK
    mode: StepMode = StepMode.AUTO
    module_id: Optional[str] = None
    handler: Optional[Callable] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    retry_delay: int = 30          # 重试间隔秒
    depends_on: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    """工作流管线定义 — 一组有序/有依赖关系的步骤。"""
    id: str
    name: str
    version: str = "1.0"
    steps: List[Step] = field(default_factory=list)
    on_complete: Optional[Callable] = None
    on_failure: Optional[Callable] = None

    def get_step(self, step_id: str) -> Optional[Step]:
        for s in self.steps:
            if s.id == step_id:
                return s
        return None

    def get_entry_steps(self) -> List[Step]:
        """获取没有依赖的入口步骤。"""
        all_deps = {d for s in self.steps for d in s.depends_on}
        return [s for s in self.steps if s.id not in all_deps]
