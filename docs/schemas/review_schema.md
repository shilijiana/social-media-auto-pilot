# 审阅域 JSON Schema 定义

> 本文件集中定义审阅域（Review Domain）的 JSON Schema，包括 ReviewTask 对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. ReviewTask（审阅任务）

### 1.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/review_task.json",
  "title": "ReviewTask",
  "description": "审阅任务 — 用于 M-11 → M-13 和 M-13 内部传递审阅任务数据",
  "type": "object",
  "required": ["task_id", "content_id", "version", "status", "review_mode"],
  "properties": {
    "task_id": {
      "type": "string",
      "pattern": "^REV-\\d{4}-\\d{6}$",
      "description": "审阅任务ID，格式 REV-YYYY-NNNNNN",
      "examples": ["REV-2026-000001"]
    },
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "被审阅的内容ID",
      "examples": ["CTN-2026-000001"]
    },
    "version": {
      "type": "string",
      "pattern": "^v\\d+$",
      "description": "审阅版本号",
      "examples": ["v1", "v2"]
    },
    "revision_items": {
      "type": "array",
      "description": "修改意见列表",
      "items": {
        "type": "object",
        "required": ["position", "opinion_type", "content", "raised_by", "raised_at"],
        "properties": {
          "position": {
            "type": "string",
            "description": "修改位置描述",
            "examples": ["第2段第3句", "00:15-00:22 片段"]
          },
          "opinion_type": {
            "type": "string",
            "enum": ["must_fix", "suggested_fix", "for_reference"],
            "description": "意见类型：must_fix=必须修改, suggested_fix=建议修改, for_reference=仅供参考"
          },
          "content": {
            "type": "string",
            "minLength": 1,
            "description": "修改意见内容"
          },
          "raised_by": {
            "type": "string",
            "description": "提出人"
          },
          "raised_at": {
            "type": "string",
            "format": "date-time",
            "examples": ["2026-07-12T16:00:00+08:00"]
          }
        }
      }
    },
    "status": {
      "type": "string",
      "enum": ["pending_review", "in_review", "needs_revision", "approved", "rejected"],
      "description": "审阅状态：pending_review=待审阅, in_review=审阅中, needs_revision=需修改, approved=已通过, rejected=已驳回"
    },
    "review_mode": {
      "type": "string",
      "enum": ["A", "B", "C"],
      "description": "审阅模式：A=严格审阅（全部检查）, B=标准审阅（重点检查）, C=快速审阅（仅合规检查）"
    },
    "review_nodes": {
      "type": "array",
      "description": "审阅节点链",
      "items": {
        "type": "object",
        "required": ["node_order", "reviewer", "status", "started_at"],
        "properties": {
          "node_order": {
            "type": "integer",
            "minimum": 1,
            "description": "节点顺序"
          },
          "reviewer": {
            "type": "string",
            "description": "审阅人"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed"],
            "description": "节点状态"
          },
          "started_at": {
            "type": "string",
            "format": "date-time"
          },
          "completed_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "deadline": {
      "type": "string",
      "format": "date-time",
      "description": "审阅截止时间"
    }
  }
}
```

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 审阅任务唯一标识，格式 REV-YYYY-NNNNNN |
| `content_id` | string | 是 | 被审阅的内容 ID |
| `version` | string | 是 | 审阅版本号 |
| `revision_items` | array | 否 | 审阅人提出的修改意见列表 |
| `revision_items[].position` | string | 是 | 修改位置描述（文本位置或视频时间） |
| `revision_items[].opinion_type` | string | 是 | 意见类型：must_fix / suggested_fix / for_reference |
| `revision_items[].content` | string | 是 | 修改意见具体内容 |
| `revision_items[].raised_by` | string | 是 | 提出修改意见的人 |
| `revision_items[].raised_at` | string | 是 | 提出时间 |
| `status` | string | 是 | 审阅任务当前状态 |
| `review_mode` | string | 是 | 审阅严格程度模式 |
| `review_nodes` | array | 否 | 多级审阅节点链 |
| `review_nodes[].node_order` | integer | 是 | 节点在链中的顺序（从1开始） |
| `review_nodes[].reviewer` | string | 是 | 该节点的审阅人 |
| `review_nodes[].status` | string | 是 | 节点状态 |
| `created_at` | string | 否 | 任务创建时间 |
| `deadline` | string | 否 | 审阅截止时间 |

### 1.3 示例

```json
{
  "task_id": "REV-2026-000001",
  "content_id": "CTN-2026-000001",
  "version": "v1",
  "revision_items": [
    {
      "position": "第1段",
      "opinion_type": "must_fix",
      "content": "开篇不够吸引人，建议加入悬念或数据",
      "raised_by": "审阅员-张三",
      "raised_at": "2026-07-12T16:00:00+08:00"
    },
    {
      "position": "00:15-00:22",
      "opinion_type": "suggested_fix",
      "content": "转场动画稍显生硬，建议使用淡入淡出",
      "raised_by": "审阅员-张三",
      "raised_at": "2026-07-12T16:05:00+08:00"
    }
  ],
  "status": "needs_revision",
  "review_mode": "B",
  "review_nodes": [
    {
      "node_order": 1,
      "reviewer": "审阅员-张三",
      "status": "completed",
      "started_at": "2026-07-12T15:30:00+08:00",
      "completed_at": "2026-07-12T16:10:00+08:00"
    }
  ],
  "created_at": "2026-07-12T15:00:00+08:00",
  "deadline": "2026-07-13T18:00:00+08:00"
}
```

### 1.4 审阅状态枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `pending_review` | 待审阅 | 任务已创建，等待审阅人开始 |
| `in_review` | 审阅中 | 审阅人正在审阅 |
| `needs_revision` | 需修改 | 审阅完成，有必须修改项 |
| `approved` | 已通过 | 审阅通过，可进入分发 |
| `rejected` | 已驳回 | 审阅驳回，需重新制作 |

### 1.5 审阅模式说明

| 模式 | 名称 | 适用场景 | 审阅范围 |
|------|------|---------|---------|
| A | 严格审阅 | 重要活动/品牌内容 | 全部维度（文案+封面+视频+合规） |
| B | 标准审阅 | 常规内容 | 重点维度（文案+合规） |
| C | 快速审阅 | 低风险内容 | 仅合规检查 |

### 1.6 意见类型枚举

| 枚举值 | 中文 | 说明 | 是否阻塞发布 |
|--------|------|------|------------|
| `must_fix` | 必须修改 | 必须修改后才能发布 | 是 |
| `suggested_fix` | 建议修改 | 建议修改，但不强制 | 否 |
| `for_reference` | 仅供参考 | 审阅人的参考意见 | 否 |

### 1.7 审阅状态机

```
pending_review ──► in_review
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      approved   rejected   needs_revision
                      │           │
                      │           └──► pending_review (修改后重新提交)
                      ▼
                  (closed)
```

### 1.8 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-11 内容精加工与定稿 | 生产者 | 创建 ReviewTask |
| M-13 分级审阅引擎 | 消费者+生产者 | 读取任务，分配审阅模式，更新状态 |
| M-14 版本变更管理 | 消费者 | 读取 revision_items 记录变更 |
| M-16 多平台分发 | 间接消费者 | 消费审阅通过的内容 |
| M-25 学习数据收集 | 消费者 | 收集审阅反馈用于自学习 |

---

## 2. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `review_tasks` | ReviewTask | M-13 |
| `review_comments` | ReviewTask.revision_items | M-13 |
| `content_versions` | ReviewTask.version | M-14 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.3 节
