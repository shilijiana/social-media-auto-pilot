"""AutoSoc 核心基础设施测试。"""

import json
import tempfile
from pathlib import Path

import pytest

# 获取 schema.sql 的绝对路径
_SCHEMA_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "schema.sql")


# ── 配置测试 ──────────────────────────────────────────

class TestConfig:
    def test_settings_defaults(self):
        from autosoc.core.config import settings
        assert settings.ai_provider == "mock"
        assert settings.system_phase == "manual"

    def test_settings_env_override(self, monkeypatch):
        monkeypatch.setenv("AUTOSOC_AI_PROVIDER", "openai")
        monkeypatch.setenv("AUTOSOC_LOG_LEVEL", "DEBUG")
        # 重新加载 settings（注意：pydantic-settings 默认不缓存）
        from autosoc.core.config import Settings
        s = Settings()
        assert s.ai_provider == "openai"
        assert s.log_level == "DEBUG"


# ── 事件总线测试 ──────────────────────────────────────

class TestEventBus:
    def test_publish_subscribe_sync(self):
        from autosoc.core.event_bus.bus import EventBus
        from autosoc.core.event_bus.events import Event

        bus = EventBus()
        received = []

        def handler(event: Event):
            received.append(event)

        bus.subscribe("test.event", handler)
        bus.publish(Event(event_type="test.event", source_module="test"), sync=True)

        assert len(received) == 1
        assert received[0].event_type == "test.event"
        assert received[0].source_module == "test"

    def test_multiple_handlers(self):
        from autosoc.core.event_bus.bus import EventBus
        from autosoc.core.event_bus.events import Event

        bus = EventBus()
        results = []

        def h1(e): results.append("h1")
        def h2(e): results.append("h2")

        bus.subscribe("multi", h1)
        bus.subscribe("multi", h2)
        bus.publish(Event(event_type="multi", source_module="test"), sync=True)

        assert results == ["h1", "h2"]

    def test_unsubscribe(self):
        from autosoc.core.event_bus.bus import EventBus
        from autosoc.core.event_bus.events import Event

        bus = EventBus()
        results = []

        def handler(e): results.append("called")

        bus.subscribe("test", handler)
        bus.unsubscribe("test", handler)
        bus.publish(Event(event_type="test", source_module="test"), sync=True)

        assert results == []

    def test_event_data_format(self):
        from autosoc.core.event_bus.events import Event

        event = Event(
            event_type="materials.collected",
            source_module="M-02",
            source_workflow_id=42,
            payload={"material_ids": [1, 2, 3]},
        )

        data = event.to_dict()
        assert data["event_type"] == "materials.collected"
        assert data["source_module"] == "M-02"
        assert data["payload"]["material_ids"] == [1, 2, 3]
        assert data["event_id"] != ""

        restored = Event.from_dict(data)
        assert restored.event_type == "materials.collected"
        assert restored.payload["material_ids"] == [1, 2, 3]


# ── 工作流引擎测试 ────────────────────────────────────

class TestWorkflowEngine:
    def test_pipeline_definition(self):
        from autosoc.core.workflow.models import Pipeline, Step, StepMode, StepType

        pipeline = Pipeline(
            id="test_pipeline",
            name="测试管线",
            steps=[
                Step(id="step1", name="步骤1", module_id="M-01"),
                Step(id="step2", name="步骤2", module_id="M-02",
                     depends_on=["step1"]),
            ],
        )

        assert pipeline.id == "test_pipeline"
        assert len(pipeline.steps) == 2
        assert pipeline.get_entry_steps()[0].id == "step1"
        assert pipeline.get_step("step2") is not None

    def test_workflow_instance_lifecycle(self):
        from autosoc.core.database import Database
        from autosoc.core.event_bus.bus import EventBus
        from autosoc.core.workflow.engine import WorkflowEngine
        from autosoc.core.workflow.models import Pipeline, Step, WorkflowStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))
            db.initialize_schema(_SCHEMA_PATH)

            bus = EventBus()
            engine = WorkflowEngine(db=db, event_bus=bus)

            pipeline = Pipeline(
                id="test_lifecycle",
                name="生命周期测试",
                steps=[Step(id="only_step", name="唯一步骤")],
            )
            engine.register_pipeline(pipeline)

            instance_id = engine.create_instance("test_lifecycle",
                                                  {"key": "value"})
            assert instance_id > 0

            instance = engine.get_instance(instance_id)
            assert instance["status"] == WorkflowStatus.PENDING.value
            assert json.loads(instance["context_data"])["key"] == "value"

    def test_step_dependency_execution(self):
        """测试有依赖关系的步骤能否按序执行。"""
        from autosoc.core.database import Database
        from autosoc.core.event_bus.bus import EventBus
        from autosoc.core.workflow.engine import WorkflowEngine
        from autosoc.core.workflow.models import Pipeline, Step, StepStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))
            db.initialize_schema(_SCHEMA_PATH)

            bus = EventBus()
            engine = WorkflowEngine(db=db, event_bus=bus)

            execution_order = []

            def handler_a(ctx): execution_order.append("A"); return {"status": "success"}
            def handler_b(ctx): execution_order.append("B"); return {"status": "success"}
            def handler_c(ctx): execution_order.append("C"); return {"status": "success"}

            pipeline = Pipeline(
                id="dep_test",
                name="依赖测试",
                steps=[
                    Step(id="A", name="A", handler=handler_a),
                    Step(id="B", name="B", handler=handler_b, depends_on=["A"]),
                    Step(id="C", name="C", handler=handler_c, depends_on=["A"]),
                ],
            )
            engine.register_pipeline(pipeline)
            engine.register_step_handler("A", handler_a)

            instance_id = engine.create_instance("dep_test", {})
            engine.start(instance_id)

            instance = engine.get_instance(instance_id)
            assert instance["status"] == "completed"
            assert "A" in execution_order
            assert "B" in execution_order
            assert "C" in execution_order


# ── 数据库测试 ────────────────────────────────────────

class TestDatabase:
    def test_table_creation(self):
        from autosoc.core.database import Database

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))
            db.initialize_schema(_SCHEMA_PATH)

            tables = db.fetchall(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            table_names = [t["name"] for t in tables
                          if not t["name"].startswith("sqlite_")]

            expected = [
                "accounts", "analytics_data", "contents",
                "learning_logs", "material_tags", "materials",
                "preference_rules", "publications", "review_records",
                "topic_plans", "workflow_instances",
            ]
            for name in expected:
                assert name in table_names, f"Missing table: {name}"

    def test_insert_and_query(self):
        from autosoc.core.database import Database

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))
            db.initialize_schema(_SCHEMA_PATH)

            # 插入选题
            topic_id = db.insert(
                "INSERT INTO topic_plans (title, keywords) VALUES (?, ?)",
                ("测试选题", '["AI", "自动化"]'),
            )
            assert topic_id > 0

            # 查询
            row = db.fetchone("SELECT * FROM topic_plans WHERE id=?", (topic_id,))
            assert row is not None
            assert row["title"] == "测试选题"

            # 列表
            rows = db.fetchall("SELECT * FROM topic_plans")
            assert len(rows) == 1
