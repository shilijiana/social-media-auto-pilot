# 分发域 JSON Schema 定义

> 本文件集中定义分发域（Distribute Domain）相关的所有 JSON Schema，包括 PublishTask 和 PerformanceData 两个核心对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. PublishTask（发布任务）

### 1.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/publish_task.json",
  "title": "PublishTask",
  "description": "发布任务 — 用于 M-16 → M-17 传递发布任务数据",
  "type": "object",
  "required": ["task_id", "content_id", "platform", "status", "scheduled_at", "retry_count"],
  "properties": {
    "task_id": {
      "type": "string",
      "pattern": "^PUB-\\d{4}-\\d{6}$",
      "description": "发布任务ID，格式 PUB-YYYY-NNNNNN",
      "examples": ["PUB-2026-000001"]
    },
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "关联内容ID",
      "examples": ["CTN-2026-000001"]
    },
    "platform": {
      "type": "string",
      "enum": ["douyin", "xiaohongshu", "bilibili", "twitter"],
      "description": "目标发布平台"
    },
    "status": {
      "type": "string",
      "enum": ["queued", "publishing", "under_review", "published", "failed", "withdrawn"],
      "description": "发布状态：queued=排队中, publishing=发布中, under_review=平台审核中, published=已发布, failed=失败, withdrawn=已撤回"
    },
    "scheduled_at": {
      "type": "string",
      "format": "date-time",
      "description": "计划发布时间",
      "examples": ["2026-07-12T20:00:00+08:00"]
    },
    "published_at": {
      "type": "string",
      "format": "date-time",
      "description": "实际发布时间"
    },
    "retry_count": {
      "type": "integer",
      "minimum": 0,
      "maximum": 5,
      "description": "重试次数"
    },
    "max_retries": {
      "type": "integer",
      "minimum": 1,
      "default": 3,
      "description": "最大重试次数"
    },
    "error_message": {
      "type": "string",
      "description": "错误信息（仅在失败时填充）"
    },
    "platform_post_id": {
      "type": "string",
      "description": "平台返回的帖子ID"
    },
    "platform_post_url": {
      "type": "string",
      "format": "uri",
      "description": "平台返回的帖子URL"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 发布任务唯一标识，格式 PUB-YYYY-NNNNNN |
| `content_id` | string | 是 | 关联的内容 ID |
| `platform` | string | 是 | 目标发布平台 |
| `status` | string | 是 | 发布任务当前状态 |
| `scheduled_at` | string | 是 | 计划发布时间 |
| `published_at` | string | 否 | 实际发布时间（发布成功后填充） |
| `retry_count` | integer | 是 | 当前已重试次数 |
| `max_retries` | integer | 否 | 最大重试次数，默认 3 |
| `error_message` | string | 否 | 失败时的错误信息 |
| `platform_post_id` | string | 否 | 平台返回的帖子/视频 ID |
| `platform_post_url` | string | 否 | 平台返回的帖子/视频 URL |
| `created_at` | string | 否 | 任务创建时间 |

### 1.3 示例

```json
{
  "task_id": "PUB-2026-000001",
  "content_id": "CTN-2026-000001",
  "platform": "douyin",
  "status": "published",
  "scheduled_at": "2026-07-12T20:00:00+08:00",
  "published_at": "2026-07-12T20:00:05+08:00",
  "retry_count": 0,
  "max_retries": 3,
  "platform_post_id": "7391234567890123456",
  "platform_post_url": "https://www.douyin.com/video/7391234567890123456",
  "created_at": "2026-07-12T18:00:00+08:00"
}
```

### 1.4 发布状态枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `queued` | 排队中 | 任务已创建，等待执行 |
| `publishing` | 发布中 | 正在调用平台 API 发布 |
| `under_review` | 平台审核中 | 已提交，平台正在审核 |
| `published` | 已发布 | 发布成功，内容已上线 |
| `failed` | 失败 | 发布失败（可重试） |
| `withdrawn` | 已撤回 | 已主动撤回发布 |

### 1.5 发布状态机

```
queued ──► publishing ──► under_review ──► published
  │            │                │               │
  └────────────┴────────────────┴───────────────┘
                     │
                     ▼
                  failed ──► queued (重试)
                     │
                     ▼
                withdrawn
```

**重试策略**: 发布失败后自动重试，使用指数退避（1s, 4s, 16s），最多重试 3 次。

### 1.6 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-16 多平台分发 | 生产者 | 创建 PublishTask |
| M-17 发布状态监控与应急响应 | 消费者+生产者 | 读取任务，执行发布，更新状态 |

---

## 2. PerformanceData（效果数据）

### 2.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/performance_data.json",
  "title": "PerformanceData",
  "description": "效果数据 — 用于 M-18 → M-20 传递内容效果指标",
  "type": "object",
  "required": ["content_id", "platform", "collected_at", "collection_node"],
  "properties": {
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "关联内容ID",
      "examples": ["CTN-2026-000001"]
    },
    "platform": {
      "type": "string",
      "enum": ["douyin", "xiaohongshu", "bilibili", "twitter"],
      "description": "发布平台"
    },
    "collected_at": {
      "type": "string",
      "format": "date-time",
      "description": "数据采集时间",
      "examples": ["2026-07-13T20:00:00+08:00"]
    },
    "collection_node": {
      "type": "string",
      "enum": ["24h", "72h", "7d", "30d"],
      "description": "采集节点"
    },
    "views": {
      "type": "integer",
      "minimum": 0,
      "description": "播放量/阅读量"
    },
    "likes": {
      "type": "integer",
      "minimum": 0,
      "description": "点赞数"
    },
    "favorites": {
      "type": "integer",
      "minimum": 0,
      "description": "收藏数"
    },
    "comments": {
      "type": "integer",
      "minimum": 0,
      "description": "评论数"
    },
    "shares": {
      "type": "integer",
      "minimum": 0,
      "description": "转发数"
    },
    "net_followers": {
      "type": "integer",
      "description": "粉丝净增（可为负）"
    },
    "watch_time": {
      "type": "number",
      "minimum": 0,
      "description": "总观看时长（秒）"
    },
    "completion_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "完播率（0-1）"
    },
    "engagement_rate": {
      "type": "number",
      "minimum": 0,
      "description": "互动率（互动总量/播放量）"
    }
  }
}
```

### 2.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content_id` | string | 是 | 关联的内容 ID |
| `platform` | string | 是 | 发布平台 |
| `collected_at` | string | 是 | 数据采集时间 |
| `collection_node` | string | 是 | 采集时间节点 |
| `views` | integer | 否 | 播放量/阅读量 |
| `likes` | integer | 否 | 点赞数 |
| `favorites` | integer | 否 | 收藏数 |
| `comments` | integer | 否 | 评论数 |
| `shares` | integer | 否 | 转发/分享数 |
| `net_followers` | integer | 否 | 该内容带来的粉丝净增量 |
| `watch_time` | number | 否 | 总观看时长（秒） |
| `completion_rate` | number | 否 | 完播率（0-1） |
| `engagement_rate` | number | 否 | 互动率 = (赞+评+转+藏)/播放量 |

### 2.3 示例

```json
{
  "content_id": "CTN-2026-000001",
  "platform": "douyin",
  "collected_at": "2026-07-13T20:00:00+08:00",
  "collection_node": "24h",
  "views": 125000,
  "likes": 8500,
  "favorites": 1200,
  "comments": 430,
  "shares": 680,
  "net_followers": 120,
  "watch_time": 1875000.0,
  "completion_rate": 0.42,
  "engagement_rate": 0.087
}
```

### 2.4 采集节点说明

| 节点 | 说明 | 采集内容 |
|------|------|---------|
| `24h` | 发布后 24 小时 | 首日数据，反映初始传播效果 |
| `72h` | 发布后 72 小时 | 传播峰值数据，反映扩散效果 |
| `7d` | 发布后 7 天 | 一周累计数据，反映长尾效果 |
| `30d` | 发布后 30 天 | 月度累计数据，反映长期价值 |

### 2.5 平台特有指标

| 平台 | 特有指标 | 说明 |
|------|---------|------|
| 抖音 | `watch_time`, `completion_rate` | 视频观看时长和完播率 |
| 小红书 | `favorites`, `saves` | 收藏和保存数据 |
| B站 | `danmaku_count`, `coins` | 弹幕数和硬币数 |
| X(Twitter) | `retweets`, `quote_tweets` | 转推和引用推文 |

### 2.6 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-18 效果数据采集 | 生产者 | 从各平台 API 采集并生成 PerformanceData |
| M-20 数据清洗与聚合 | 消费者 | 读取原始数据进行清洗和聚合 |
| M-25 学习数据收集 | 消费者 | 收集效果数据用于自学习 |
| M-30 学习成效量化与报告 | 间接消费者 | 评估规则应用后的效果变化 |

---

## 3. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `publish_tasks` | PublishTask | M-16, M-17 |
| `publish_logs` | PublishTask (日志) | M-17 |
| `performance_metrics` | PerformanceData | M-18 |
| `account_health` | (独立 Schema) | M-19 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.4 节
