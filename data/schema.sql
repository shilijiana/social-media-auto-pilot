-- AutoSoc 数据库 Schema — SQLite 兼容 DDL
-- 所有表使用 WAL 模式，主键统一 INTEGER PRIMARY KEY AUTOINCREMENT

-- ── 1. 选题计划表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS topic_plans (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    description      TEXT DEFAULT '',
    source           TEXT NOT NULL DEFAULT 'manual',
    keywords         TEXT NOT NULL DEFAULT '[]',
    target_platforms TEXT NOT NULL DEFAULT '[]',
    priority         INTEGER NOT NULL DEFAULT 3,
    status           TEXT NOT NULL DEFAULT 'draft',
    planned_date     TEXT,
    actual_date      TEXT,
    parent_plan_id   INTEGER REFERENCES topic_plans(id),
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_topic_plans_status ON topic_plans(status);
CREATE INDEX IF NOT EXISTS idx_topic_plans_planned_date ON topic_plans(planned_date);

-- ── 2. 素材表 ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS materials (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_plan_id   INTEGER NOT NULL REFERENCES topic_plans(id),
    material_type   TEXT NOT NULL,
    source_url      TEXT DEFAULT '',
    local_path      TEXT DEFAULT '',
    content_hash    TEXT NOT NULL,
    title           TEXT DEFAULT '',
    metadata        TEXT DEFAULT '{}',
    quality_score   REAL DEFAULT 0.0,
    copyright_info  TEXT DEFAULT '{}',
    dedup_status    TEXT DEFAULT 'pending',
    status          TEXT DEFAULT 'active',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_materials_topic_plan ON materials(topic_plan_id);
CREATE INDEX IF NOT EXISTS idx_materials_type ON materials(material_type);
CREATE INDEX IF NOT EXISTS idx_materials_hash ON materials(content_hash);

-- ── 3. 素材标签表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS material_tags (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id     INTEGER NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    tag             TEXT NOT NULL,
    tag_type        TEXT NOT NULL DEFAULT 'auto',
    confidence      REAL DEFAULT 0.0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(material_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_material_tags_tag ON material_tags(tag);
CREATE INDEX IF NOT EXISTS idx_material_tags_material ON material_tags(material_id);

-- ── 4. 内容版本表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS contents (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_plan_id    INTEGER NOT NULL REFERENCES topic_plans(id),
    version          INTEGER NOT NULL DEFAULT 1,
    title            TEXT DEFAULT '',
    body_text        TEXT DEFAULT '',
    image_path       TEXT DEFAULT '',
    video_path       TEXT DEFAULT '',
    platform_config  TEXT DEFAULT '{}',
    editing_params   TEXT DEFAULT '{}',
    compliance_result TEXT DEFAULT '{}',
    status           TEXT NOT NULL DEFAULT 'draft',
    review_decision  TEXT DEFAULT '',
    created_by       TEXT DEFAULT 'system',
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_contents_topic_plan ON contents(topic_plan_id);
CREATE INDEX IF NOT EXISTS idx_contents_status ON contents(status);

-- ── 5. 发布记录表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS publications (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id       INTEGER NOT NULL REFERENCES contents(id),
    platform         TEXT NOT NULL,
    account_id       INTEGER NOT NULL REFERENCES accounts(id),
    scheduled_time   TEXT,
    published_time   TEXT,
    status           TEXT NOT NULL DEFAULT 'pending',
    failure_reason   TEXT DEFAULT '',
    platform_post_id TEXT DEFAULT '',
    platform_url     TEXT DEFAULT '',
    retry_count      INTEGER DEFAULT 0,
    browser_snapshot TEXT DEFAULT '',
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_publications_content ON publications(content_id);
CREATE INDEX IF NOT EXISTS idx_publications_platform ON publications(platform);
CREATE INDEX IF NOT EXISTS idx_publications_status ON publications(status);

-- ── 6. 账号表 ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accounts (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    platform         TEXT NOT NULL,
    account_name     TEXT NOT NULL,
    cookie_store     TEXT DEFAULT '',
    proxy_config     TEXT DEFAULT '{}',
    health_status    TEXT DEFAULT 'good',
    health_score     REAL DEFAULT 1.0,
    daily_post_count INTEGER DEFAULT 0,
    daily_limit      INTEGER DEFAULT 5,
    last_post_time   TEXT,
    is_active        INTEGER DEFAULT 1,
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_accounts_platform ON accounts(platform);
CREATE INDEX IF NOT EXISTS idx_accounts_health ON accounts(health_status);

-- ── 7. 分析数据表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS analytics_data (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_id   INTEGER NOT NULL REFERENCES publications(id),
    platform         TEXT NOT NULL,
    collected_at     TEXT NOT NULL,
    data_category    TEXT NOT NULL,
    raw_data         TEXT DEFAULT '{}',
    processed_data   TEXT DEFAULT '{}',
    metrics          TEXT DEFAULT '{}',
    data_version     INTEGER DEFAULT 1,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_analytics_publication ON analytics_data(publication_id);
CREATE INDEX IF NOT EXISTS idx_analytics_collected ON analytics_data(collected_at);
CREATE INDEX IF NOT EXISTS idx_analytics_category ON analytics_data(data_category);

-- ── 8. 审阅记录表 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS review_records (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id       INTEGER NOT NULL REFERENCES contents(id),
    review_level     INTEGER NOT NULL DEFAULT 0,
    decision         TEXT NOT NULL,
    reviewer         TEXT DEFAULT '',
    comments         TEXT DEFAULT '',
    auto_confidence  REAL DEFAULT 0.0,
    human_reviewed   INTEGER DEFAULT 0,
    reviewed_at      TEXT NOT NULL DEFAULT (datetime('now')),
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_review_content ON review_records(content_id);
CREATE INDEX IF NOT EXISTS idx_review_level ON review_records(review_level);
CREATE INDEX IF NOT EXISTS idx_review_decision ON review_records(decision);

-- ── 9. 偏好规则库 ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS preference_rules (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type        TEXT NOT NULL,
    rule_name        TEXT NOT NULL,
    rule_value       TEXT NOT NULL,
    weight           REAL DEFAULT 1.0,
    source           TEXT DEFAULT 'manual',
    confidence       REAL DEFAULT 1.0,
    ttl_seconds      INTEGER DEFAULT 0,
    expires_at       TEXT,
    is_active        INTEGER DEFAULT 1,
    applied_count    INTEGER DEFAULT 0,
    effect_score     REAL DEFAULT 0.0,
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pref_rules_type ON preference_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_pref_rules_active ON preference_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_pref_rules_expires ON preference_rules(expires_at);

-- ── 10. 学习日志表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS learning_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT NOT NULL,
    rule_id          INTEGER REFERENCES preference_rules(id),
    event_type       TEXT NOT NULL,
    before_value     TEXT DEFAULT '{}',
    after_value      TEXT DEFAULT '{}',
    triggered_by     TEXT DEFAULT '',
    metadata         TEXT DEFAULT '{}',
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_learning_session ON learning_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_rule ON learning_logs(rule_id);
CREATE INDEX IF NOT EXISTS idx_learning_event ON learning_logs(event_type);

-- ── 11. 工作流实例表 ──────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow_instances (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_type    TEXT NOT NULL,
    topic_plan_id    INTEGER REFERENCES topic_plans(id),
    status           TEXT NOT NULL DEFAULT 'pending',
    current_step     TEXT DEFAULT '',
    step_states      TEXT DEFAULT '{}',
    context_data     TEXT DEFAULT '{}',
    error_info       TEXT DEFAULT '{}',
    error_count      INTEGER DEFAULT 0,
    started_at       TEXT,
    completed_at     TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_instances(status);
CREATE INDEX IF NOT EXISTS idx_workflow_type ON workflow_instances(workflow_type);
CREATE INDEX IF NOT EXISTS idx_workflow_topic ON workflow_instances(topic_plan_id);
