# 内容域 JSON Schema 定义

> 本文件集中定义内容域（Content Domain）相关的所有 JSON Schema，包括 Content 和 ComplianceResult 两个核心对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. Content（内容对象）

### 1.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/content.json",
  "title": "Content",
  "description": "内容对象 — 用于 M-07→M-08、M-08→M-11、M-11、M-13→M-16 之间传递内容数据",
  "type": "object",
  "required": ["content_id", "topic_id", "platform", "copytext", "tags"],
  "properties": {
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "内容ID，格式 CTN-YYYY-NNNNNN",
      "examples": ["CTN-2026-000001"]
    },
    "topic_id": {
      "type": "string",
      "pattern": "^T\\d{4}-\\d{3}$",
      "description": "关联选题编号",
      "examples": ["T2026-001"]
    },
    "platform": {
      "type": "string",
      "enum": ["douyin", "xiaohongshu", "bilibili", "twitter"],
      "description": "目标发布平台"
    },
    "copytext": {
      "type": "string",
      "minLength": 1,
      "description": "文案正文",
      "examples": ["AI 正在改变我们的生活..."]
    },
    "title": {
      "type": "string",
      "description": "内容标题（B站/小红书适用）"
    },
    "cover_path": {
      "type": "string",
      "description": "封面图存储路径"
    },
    "video_path": {
      "type": "string",
      "description": "视频文件存储路径"
    },
    "tags": {
      "type": "array",
      "description": "内容标签列表",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "minItems": 1
    },
    "material_refs": {
      "type": "array",
      "description": "引用的素材ID列表",
      "items": {
        "type": "string",
        "pattern": "^MAT-\\d{4}-\\d{6}$"
      }
    },
    "version": {
      "type": "string",
      "pattern": "^v\\d+$",
      "description": "内容版本号",
      "examples": ["v1", "v2"]
    },
    "status": {
      "type": "string",
      "enum": [
        "draft",
        "compliance_checking",
        "compliance_passed",
        "compliance_failed",
        "pending_review",
        "review_approved",
        "review_rejected",
        "ready_to_publish",
        "published"
      ],
      "description": "内容状态"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "examples": ["2026-07-12T10:30:00+08:00"]
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "examples": ["2026-07-12T15:00:00+08:00"]
    }
  }
}
```

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content_id` | string | 是 | 内容唯一标识，格式 CTN-YYYY-NNNNNN |
| `topic_id` | string | 是 | 关联的选题计划编号 |
| `platform` | string | 是 | 目标发布平台 |
| `copytext` | string | 是 | 文案正文内容 |
| `title` | string | 否 | 标题（B站/小红书需要） |
| `cover_path` | string | 否 | 封面图文件路径 |
| `video_path` | string | 否 | 视频文件路径 |
| `tags` | string[] | 是 | 内容标签 |
| `material_refs` | string[] | 否 | 引用的素材 ID 列表 |
| `version` | string | 否 | 内容版本号，如 v1, v2 |
| `status` | string | 否 | 内容生命周期状态 |
| `created_at` | string | 否 | 创建时间 |
| `updated_at` | string | 否 | 最后更新时间 |

### 1.3 示例

```json
{
  "content_id": "CTN-2026-000001",
  "topic_id": "T2026-001",
  "platform": "douyin",
  "copytext": "2026年，AI正在以惊人的速度改变我们的日常生活。从智能助手到自动驾驶，技术的边界不断被突破。#AI #科技",
  "title": "",
  "cover_path": "covers/2026/07/CTN-2026-000001_cover.png",
  "video_path": "videos/2026/07/CTN-2026-000001_video.mp4",
  "tags": ["AI", "科技", "未来"],
  "material_refs": ["MAT-2026-000001", "MAT-2026-000003"],
  "version": "v1",
  "status": "pending_review",
  "created_at": "2026-07-12T10:30:00+08:00",
  "updated_at": "2026-07-12T15:00:00+08:00"
}
```

### 1.4 内容状态枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `draft` | 草稿 | 内容正在编辑中 |
| `compliance_checking` | 合规检查中 | 正在执行合规性检查 |
| `compliance_passed` | 合规通过 | 合规检查通过 |
| `compliance_failed` | 合规未通过 | 合规检查未通过，需修改 |
| `pending_review` | 待审阅 | 等待人工审阅 |
| `review_approved` | 审阅通过 | 人工审阅已通过 |
| `review_rejected` | 审阅驳回 | 人工审阅未通过 |
| `ready_to_publish` | 待发布 | 已就绪，等待发布 |
| `published` | 已发布 | 已成功发布到平台 |

### 1.5 内容状态机

```
draft
  │
  ▼
compliance_checking
  │
  ├──► compliance_passed ──► pending_review
  │                              │
  │              ┌───────────────┼───────────────┐
  │              ▼               ▼               ▼
  │        review_approved  review_rejected  in_review
  │              │               │
  │              │               └──► draft (返修)
  │              ▼
  │        ready_to_publish
  │              │
  │              ▼
  │          published
  │
  └──► compliance_failed ──► draft (返修)
```

### 1.6 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-07 素材匹配与调用 | 生产者 | 创建 Content 草稿（partial） |
| M-08 文案差异化生成 | 消费者+生产者 | 读取草稿，填充 copytext |
| M-09 封面图生成 | 消费者+生产者 | 读取内容，填充 cover_path |
| M-10 视频初剪 | 消费者+生产者 | 读取内容，填充 video_path |
| M-11 内容精加工与定稿 | 消费者+生产者 | 最终润色，更新 status |
| M-12 合规性自检 | 消费者 | 读取内容进行合规检查 |
| M-13 分级审阅引擎 | 消费者 | 读取内容创建审阅任务 |
| M-16 多平台分发 | 消费者 | 读取审阅通过的内容进行分发 |

---

## 2. ComplianceResult（合规检查结果）

### 2.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/compliance_result.json",
  "title": "ComplianceResult",
  "description": "合规检查结果 — 用于 M-12 → M-11 传递合规检查报告",
  "type": "object",
  "required": ["check_id", "content_id", "check_items", "overall_passed", "checked_at"],
  "properties": {
    "check_id": {
      "type": "string",
      "pattern": "^CHK-\\d{4}-\\d{6}$",
      "description": "检查ID，格式 CHK-YYYY-NNNNNN",
      "examples": ["CHK-2026-000001"]
    },
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "被检查的内容ID",
      "examples": ["CTN-2026-000001"]
    },
    "check_items": {
      "type": "array",
      "description": "检查项列表",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["rule_id", "rule_name", "passed", "detail"],
        "properties": {
          "rule_id": {
            "type": "string",
            "description": "规则ID"
          },
          "rule_name": {
            "type": "string",
            "description": "规则名称"
          },
          "passed": {
            "type": "boolean",
            "description": "是否通过"
          },
          "detail": {
            "type": "string",
            "description": "检查详情"
          },
          "suggestion": {
            "type": "string",
            "description": "修改建议"
          }
        }
      }
    },
    "overall_passed": {
      "type": "boolean",
      "description": "整体是否通过"
    },
    "checked_at": {
      "type": "string",
      "format": "date-time",
      "description": "检查时间",
      "examples": ["2026-07-12T14:30:00+08:00"]
    }
  }
}
```

### 2.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `check_id` | string | 是 | 检查唯一标识，格式 CHK-YYYY-NNNNNN |
| `content_id` | string | 是 | 被检查的内容 ID |
| `check_items` | array | 是 | 各项检查结果列表 |
| `check_items[].rule_id` | string | 是 | 检查规则 ID |
| `check_items[].rule_name` | string | 是 | 规则名称 |
| `check_items[].passed` | boolean | 是 | 该项是否通过 |
| `check_items[].detail` | string | 是 | 检查详情说明 |
| `check_items[].suggestion` | string | 否 | 不通过时的修改建议 |
| `overall_passed` | boolean | 是 | 全部检查项是否通过 |
| `checked_at` | string | 是 | 检查执行时间 |

### 2.3 示例

```json
{
  "check_id": "CHK-2026-000001",
  "content_id": "CTN-2026-000001",
  "check_items": [
    {
      "rule_id": "CMP-001",
      "rule_name": "敏感词检测",
      "passed": true,
      "detail": "未检测到敏感词"
    },
    {
      "rule_id": "CMP-002",
      "rule_name": "广告法合规",
      "passed": false,
      "detail": "文案中含'最'字，可能违反广告法",
      "suggestion": "将'最先进的技术'修改为'前沿技术'"
    },
    {
      "rule_id": "CMP-003",
      "rule_name": "版权素材检查",
      "passed": true,
      "detail": "所有引用素材版权状态正常"
    }
  ],
  "overall_passed": false,
  "checked_at": "2026-07-12T14:30:00+08:00"
}
```

### 2.4 内置检查规则 ID

| 规则 ID | 名称 | 来源 |
|---------|------|------|
| CMP-001 | 敏感词检测 | compliance_rules.yaml → sensitive_words |
| CMP-002 | 广告法合规 | compliance_rules.yaml → sensitive_words |
| CMP-003 | 版权素材检查 | Material.copyright_status |
| CMP-004 | 平台规则检查 | compliance_rules.yaml → platform_rules |

### 2.5 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-12 合规性自检 | 生产者 | 执行检查并生成 ComplianceResult |
| M-11 内容精加工与定稿 | 消费者 | 读取检查结果，决定是否需要修改 |

---

## 3. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `content_drafts` | Content | M-08, M-11 |
| `cover_images` | Content.cover_path | M-09 |
| `video_drafts` | Content.video_path | M-10, M-11 |
| `compliance_checks` | ComplianceResult | M-12 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.2 节
