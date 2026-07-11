"""AutoSoc 事件定义 — 所有系统事件的类型常量与 Event 数据类。"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


# ── 事件类型常量 ──────────────────────────────────────

# 素材采集域
TOPIC_PLAN_APPROVED = "topic_plan.approved"
MATERIALS_COLLECTED = "materials.collected"
MATERIALS_REVIEWED = "materials.reviewed"

# 内容生产域
CONTENT_DRAFT_READY = "content.draft_ready"
CONTENT_REVIEWED = "content.reviewed"
CONTENT_FINALIZED = "content.finalized"

# 分发与数据域
CONTENT_PUBLISHED = "content.published"
PUBLICATION_FAILED = "publication.failed"
DATA_COLLECTED = "data.collected"

# 数据分析域
DATA_ANALYZED = "data.analyzed"
PLAN_DRAFT_READY = "plan.draft_ready"
PLAN_APPROVED = "plan.approved"

# 自学习域
LEARNING_RULE_UPDATED = "learning.rule_updated"

# 系统事件
SYSTEM_STARTUP = "system.startup"
SYSTEM_SHUTDOWN = "system.shutdown"
SYSTEM_ERROR = "system.error"


@dataclass
class Event:
    """通用事件数据标准格式。所有模块间通信均使用此结构。"""

    event_type: str
    source_module: str
    source_workflow_id: Optional[int] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    event_id: str = field(default_factory=lambda: uuid4().hex[:12])
    correlation_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "source_module": self.source_module,
            "source_workflow_id": self.source_workflow_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(**data)
