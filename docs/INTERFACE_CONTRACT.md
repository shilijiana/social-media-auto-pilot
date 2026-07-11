# Hermes 模块间接口契约

> **文档性质**：模块间数据格式的唯一权威来源（Single Source of Truth）
> **目标受众**：Hermes Agent（自动编码与集成）
> **最后更新**：2026-07-12
> **版本**：v1.0

---

## 1. 全局约定

### 1.1 数据交换格式

所有模块间的数据交换统一使用 **JSON** 格式。

### 1.2 时间格式

所有时间字段统一使用 **ISO 8601 含时区** 格式：

```
"2026-07-12T10:30:00+08:00"
```

### 1.3 状态字段

所有状态字段使用 **英文枚举值**，格式为 `lowercase_snake_case`：

```
✅ 正确：pending_review, in_progress, quality_passed
❌ 错误：待审阅, PendingReview, qualityPassed
```

### 1.4 ID 格式

所有 ID 均为 **字符串** 类型。各类型 ID 遵循固定格式：

| ID 类型 | 格式 | 示例 | 说明 |
|---|---|---|---|
| 选题编号 | T + YYYY + - + 3位序列号 | `T2026-001` | 选题计划标识 |
| 素材ID | MAT-YYYY-NNNNNN | `MAT-2026-000001` | 素材唯一标识 |
| 内容ID | CTN-YYYY-NNNNNN | `CTN-2026-000001` | 内容唯一标识 |
| 审阅任务ID | REV-YYYY-NNNNNN | `REV-2026-000001` | 审阅任务标识 |
| 发布任务ID | PUB-YYYY-NNNNNN | `PUB-2026-000001` | 发布任务标识 |
| 报告ID | RPT-YYYY-NNNNNN | `RPT-2026-000001` | 报告标识 |
| 规则ID | RUL-YYYY-NNNNNN | `RUL-2026-000001` | 偏好规则标识 |
| 检查ID | CHK-YYYY-NNNNNN | `CHK-2026-000001` | 合规检查标识 |

---

## 2. 文件命名规范

### 2.1 标准格式

```
[选题编号]_[模块名]_[平台]_[版本号]_[日期].扩展名
```

### 2.2 各部分说明

| 组成部分 | 格式 | 示例 | 说明 |
|---|---|---|---|
| 选题编号 | T + YYYY + - + 3位序列号 | `T2026-001` | 选题计划标识 |
| 模块名 | M + 2位数字 | `M08` | 模块编号 |
| 平台 | 小写英文平台名 | `douyin`, `xiaohongshu`, `bilibili`, `twitter` | 目标平台 |
| 版本号 | v + 数字 | `v2` | 迭代版本 |
| 日期 | YYYYMMDD | `20260712` | 生成日期 |
| 扩展名 | json / png / mp4 / txt | 见下方说明 | 文件类型 |

### 2.3 命名示例

```
T2026-001_M08_douyin_v2_20260712.json      # 文案草稿
T2026-001_M09_douyin_v1_20260712.png        # 封面图
T2026-001_M10_douyin_v1_20260712.mp4        # 视频草稿
T2026-001_M16_douyin_v1_20260712.json       # 发布任务
T2026-001_M18_douyin_v1_20260712.json       # 效果数据
```

---

## 3. 数据库表与模块映射

| 数据库表 | 对应模块 | 说明 |
|---|---|---|
| `topics` | M-01 | 选题计划表 |
| `keywords` | M-01 | 关键词表 |
| `materials` | M-02, M-03, M-06 | 素材主表 |
| `material_tags` | M-06 | 素材标签关联 |
| `copyright_records` | M-06 | 版权记录 |
| `content_drafts` | M-08, M-11 | 内容草稿 |
| `cover_images` | M-09 | 封面图 |
| `video_drafts` | M-10, M-11 | 视频草稿 |
| `compliance_checks` | M-12 | 合规检查 |
| `review_tasks` | M-13 | 审阅任务 |
| `review_comments` | M-13 | 审阅意见 |
| `content_versions` | M-14 | 版本记录 |
| `common_materials` | M-15 | 通用素材池 |
| `publish_tasks` | M-16, M-17 | 发布任务 |
| `publish_logs` | M-17 | 发布日志 |
| `performance_metrics` | M-18 | 效果数据 |
| `account_health` | M-19 | 账号健康度 |
| `analytics_reports` | M-20, M-21 | 分析报告 |
| `comment_analysis` | M-22 | 评论分析 |
| `hot_topics` | M-23 | 热点话题 |
| `plan_drafts` | M-24 | 计划草案 |
| `learning_records` | M-25 | 学习记录 |
| `preference_rules` | M-26, M-27 | 偏好规则 |
| `preference_templates` | M-28 | 偏好模板 |
| `learning_reports` | M-30 | 学习报告 |

---

## 4. JSON Schema 定义

### 4.1 素材域（Material Domain）

#### 4.1.1 Material（素材对象）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/material.json",
  "title": "Material",
  "description": "素材对象 — 用于模块 M-02、M-03、M-06、M-07、M-15 之间传递素材数据",
  "type": "object",
  "required": ["material_id", "type", "path", "copyright_status", "resolution", "file_size", "clarity_score", "collected_at"],
  "properties": {
    "material_id": {
      "type": "string",
      "pattern": "^MAT-\\d{4}-\\d{6}$",
      "description": "素材ID，格式 MAT-YYYY-NNNNNN",
      "examples": ["MAT-2026-000001"]
    },
    "topic_id": {
      "type": "string",
      "pattern": "^T\\d{4}-\\d{3}$",
      "description": "关联选题编号",
      "examples": ["T2026-001"]
    },
    "type": {
      "type": "string",
      "enum": ["image", "video", "audio", "text"],
      "description": "素材类型"
    },
    "path": {
      "type": "string",
      "description": "素材存储路径（对象存储 Key）",
      "examples": ["materials/2026/07/MAT-2026-000001/image_001.jpg"]
    },
    "tags": {
      "type": "array",
      "description": "素材标签列表",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "minItems": 1,
      "examples": [["科技", "AI", "产品发布"]]
    },
    "copyright_status": {
      "type": "string",
      "enum": ["free", "licensed", "expiring", "expired", "unknown"],
      "description": "版权状态：free=免费可商用, licensed=已授权, expiring=即将到期, expired=已过期, unknown=未知"
    },
    "resolution": {
      "type": "object",
      "required": ["width", "height"],
      "properties": {
        "width": {
          "type": "integer",
          "minimum": 1,
          "description": "宽度（像素）"
        },
        "height": {
          "type": "integer",
          "minimum": 1,
          "description": "高度（像素）"
        }
      }
    },
    "file_size": {
      "type": "integer",
      "minimum": 1,
      "description": "文件大小（字节）"
    },
    "clarity_score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "清晰度评分（0-100）"
    },
    "source_url": {
      "type": "string",
      "format": "uri",
      "description": "素材来源URL"
    },
    "collected_at": {
      "type": "string",
      "format": "date-time",
      "description": "素材采集时间（ISO 8601 含时区）",
      "examples": ["2026-07-12T10:30:00+08:00"]
    },
    "license_expiry": {
      "type": "string",
      "format": "date-time",
      "description": "授权到期日（仅 licensed/expiring 状态时必填）",
      "examples": ["2027-07-12T00:00:00+08:00"]
    },
    "platform": {
      "type": "string",
      "enum": ["douyin", "xiaohongshu", "bilibili", "twitter"],
      "description": "采集来源平台"
    },
    "duration": {
      "type": "number",
      "minimum": 0,
      "description": "时长（秒），仅 video/audio 类型有效"
    },
    "thumbnail_path": {
      "type": "string",
      "description": "缩略图路径"
    }
  }
}
```

**示例 JSON：**

```json
{
  "material_id": "MAT-2026-000001",
  "topic_id": "T2026-001",
  "type": "image",
  "path": "materials/2026/07/MAT-2026-000001/hero_banner.jpg",
  "tags": ["科技", "AI", "发布会"],
  "copyright_status": "free",
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "file_size": 2457600,
  "clarity_score": 92,
  "source_url": "https://example.com/images/hero_banner.jpg",
  "collected_at": "2026-07-12T10:30:00+08:00",
  "platform": "douyin",
  "thumbnail_path": "materials/2026/07/MAT-2026-000001/hero_banner_thumb.jpg"
}
```

---

#### 4.1.2 Keyword（关键词对象）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/keyword.json",
  "title": "Keyword",
  "description": "关键词对象 — 用于 M-01 → M-02 的关键词扩展数据传递",
  "type": "object",
  "required": ["original_word", "expanded_words", "platform"],
  "properties": {
    "original_word": {
      "type": "string",
      "minLength": 1,
      "description": "原始关键词",
      "examples": ["人工智能"]
    },
    "expanded_words": {
      "type": "array",
      "description": "扩展词列表",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["word", "type", "relevance"],
        "properties": {
          "word": {
            "type": "string",
            "minLength": 1,
            "description": "扩展词"
          },
          "type": {
            "type": "string",
            "enum": ["synonym", "related", "long_tail"],
            "description": "扩展类型：synonym=同义词, related=相关词, long_tail=长尾词"
          },
          "relevance": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "与原词关联度（0-1）"
          }
        }
      }
    },
    "platform": {
      "type": "string",
      "enum": ["douyin", "xiaohongshu", "bilibili", "twitter"],
      "description": "目标平台"
    },
    "topic_id": {
      "type": "string",
      "pattern": "^T\\d{4}-\\d{3}$",
      "description": "关联选题编号"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "生成时间",
      "examples": ["2026-07-12T10:30:00+08:00"]
    }
  }
}
```

**示例 JSON：**

```json
{
  "original_word": "人工智能",
  "expanded_words": [
    {
      "word": "AI",
      "type": "synonym",
      "relevance": 0.98
    },
    {
      "word": "大模型",
      "type": "related",
      "relevance": 0.85
    },
    {
      "word": "人工智能发展趋势2026",
      "type": "long_tail",
      "relevance": 0.72
    }
  ],
  "platform": "douyin",
  "topic_id": "T2026-001",
  "created_at": "2026-07-12T10:30:00+08:00"
}
```

---

### 4.2 内容域（Content Domain）

#### 4.2.1 Content（内容对象）

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
      "enum": ["draft", "compliance_checking", "compliance_passed", "compliance_failed", "pending_review", "review_approved", "review_rejected", "ready_to_publish", "published"],
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

**示例 JSON：**

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

---

#### 4.2.2 ComplianceResult（合规检查结果）

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

**示例 JSON：**

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

---

### 4.3 审阅域（Review Domain）

#### 4.3.1 ReviewTask（审阅任务）

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
            "description": "审���人"
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

**示例 JSON：**

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

---

### 4.4 分发域（Distribute Domain）

#### 4.4.1 PublishTask（发布任务）

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

**示例 JSON：**

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

---

#### 4.4.2 PerformanceData（效果数据）

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

**示例 JSON：**

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

---

### 4.5 分析域（Analytics Domain）

#### 4.5.1 AnalyticsReport（分析报告）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/analytics_report.json",
  "title": "AnalyticsReport",
  "description": "分析报告 — 用于 M-20,M-21,M-22,M-23 → M-24 传递综合分析数据",
  "type": "object",
  "required": ["report_id", "report_type", "generated_at", "period"],
  "properties": {
    "report_id": {
      "type": "string",
      "pattern": "^RPT-\\d{4}-\\d{6}$",
      "description": "报告ID，格式 RPT-YYYY-NNNNNN",
      "examples": ["RPT-2026-000001"]
    },
    "report_type": {
      "type": "string",
      "enum": ["daily", "weekly", "monthly", "per_content"],
      "description": "报告类型：daily=日报, weekly=周报, monthly=月报, per_content=单内容分析"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time",
      "description": "报告生成时间",
      "examples": ["2026-07-13T09:00:00+08:00"]
    },
    "period": {
      "type": "object",
      "required": ["start", "end"],
      "properties": {
        "start": {
          "type": "string",
          "format": "date",
          "description": "统计周期开始日期",
          "examples": ["2026-07-06"]
        },
        "end": {
          "type": "string",
          "format": "date",
          "description": "统计周期结束日期",
          "examples": ["2026-07-12"]
        }
      }
    },
    "metrics_summary": {
      "type": "object",
      "description": "指标汇总（key 为指标名，value 为指标值）",
      "examples": [{
        "total_views": 2500000,
        "total_likes": 120000,
        "avg_engagement_rate": 0.065,
        "total_posts": 14,
        "new_followers": 2300
      }]
    },
    "horizontal_comparison": {
      "type": "object",
      "description": "横向对比（平台间对比），key 为平台名，value 为指标对象",
      "examples": [{
        "douyin": { "views": 1800000, "engagement_rate": 0.072 },
        "xiaohongshu": { "views": 500000, "engagement_rate": 0.058 },
        "bilibili": { "views": 200000, "engagement_rate": 0.045 }
      }]
    },
    "vertical_comparison": {
      "type": "object",
      "description": "纵向对比（与上一周期对比），key 为指标名，value 包含当前值和变化率",
      "examples": [{
        "total_views": { "current": 2500000, "previous": 2100000, "change_rate": 0.19 },
        "engagement_rate": { "current": 0.065, "previous": 0.058, "change_rate": 0.12 }
      }]
    },
    "hotspot_analysis": {
      "type": "object",
      "description": "热点分析",
      "properties": {
        "trending_topics": {
          "type": "array",
          "description": "热门话题",
          "items": {
            "type": "object",
            "properties": {
              "topic": { "type": "string" },
              "heat_score": { "type": "integer", "minimum": 0, "maximum": 100 },
              "platform": { "type": "string" }
            }
          }
        },
        "high_performers": {
          "type": "array",
          "description": "高表现内容ID列表",
          "items": {
            "type": "string",
            "pattern": "^CTN-\\d{4}-\\d{6}$"
          }
        }
      }
    },
    "suggestions": {
      "type": "array",
      "description": "改进建议",
      "items": {
        "type": "object",
        "required": ["category", "content"],
        "properties": {
          "category": {
            "type": "string",
            "enum": ["content", "timing", "platform", "style", "interaction"],
            "description": "建议类别"
          },
          "content": {
            "type": "string",
            "description": "建议内容"
          },
          "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "优先级"
          },
          "expected_impact": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "预期影响度（0-1）"
          }
        }
      }
    }
  }
}
```

**示例 JSON：**

```json
{
  "report_id": "RPT-2026-000001",
  "report_type": "weekly",
  "generated_at": "2026-07-13T09:00:00+08:00",
  "period": {
    "start": "2026-07-06",
    "end": "2026-07-12"
  },
  "metrics_summary": {
    "total_views": 2500000,
    "total_likes": 120000,
    "total_favorites": 18000,
    "total_comments": 6500,
    "total_shares": 9500,
    "avg_engagement_rate": 0.065,
    "total_posts": 14,
    "new_followers": 2300
  },
  "horizontal_comparison": {
    "douyin": { "views": 1800000, "engagement_rate": 0.072 },
    "xiaohongshu": { "views": 500000, "engagement_rate": 0.058 },
    "bilibili": { "views": 200000, "engagement_rate": 0.045 }
  },
  "vertical_comparison": {
    "total_views": { "current": 2500000, "previous": 2100000, "change_rate": 0.19 },
    "engagement_rate": { "current": 0.065, "previous": 0.058, "change_rate": 0.12 },
    "new_followers": { "current": 2300, "previous": 1800, "change_rate": 0.28 }
  },
  "hotspot_analysis": {
    "trending_topics": [
      { "topic": "AI大模型应用", "heat_score": 92, "platform": "douyin" },
      { "topic": "智能家居新品", "heat_score": 85, "platform": "xiaohongshu" }
    ],
    "high_performers": ["CTN-2026-000001", "CTN-2026-000005", "CTN-2026-000009"]
  },
  "suggestions": [
    {
      "category": "timing",
      "content": "本周数据显示晚8点发布的视频互动率比下午发布高23%，建议核心内容安排在晚间发布",
      "priority": "high",
      "expected_impact": 0.75
    },
    {
      "category": "content",
      "content": "AI话题内容平均互动率比行业平均值高40%，建议加大AI相关选题比例",
      "priority": "medium",
      "expected_impact": 0.60
    }
  ]
}
```

---

### 4.6 学习域（Learning Domain）

#### 4.6.1 PreferenceRule（偏好规则）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/preference_rule.json",
  "title": "PreferenceRule",
  "description": "偏好规则 — 用于 M-26、M-27、M-29 传递偏好规则数据",
  "type": "object",
  "required": ["rule_id", "preference_type", "rule_content", "confidence", "sources", "created_at", "status", "weight"],
  "properties": {
    "rule_id": {
      "type": "string",
      "pattern": "^RUL-\\d{4}-\\d{6}$",
      "description": "规则ID，格式 RUL-YYYY-NNNNNN",
      "examples": ["RUL-2026-000001"]
    },
    "preference_type": {
      "type": "string",
      "enum": ["content", "visual", "strategy"],
      "description": "偏好类型：content=内容偏好, visual=视觉偏好, strategy=策略偏好"
    },
    "rule_content": {
      "type": "string",
      "minLength": 1,
      "description": "规则内容（自然语言描述）",
      "examples": ["用户偏好开头带数字/数据的标题风格"]
    },
    "confidence": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "置信度（0-100）"
    },
    "sources": {
      "type": "array",
      "description": "规则来源列表",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "examples": [["review_history", "performance_data"]]
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "规则创建时间",
      "examples": ["2026-07-12T10:00:00+08:00"]
    },
    "last_updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "最后更新时间",
      "examples": ["2026-07-12T18:00:00+08:00"]
    },
    "status": {
      "type": "string",
      "enum": ["active", "degraded", "paused", "deleted"],
      "description": "规则状态：active=生效中, degraded=降级（置信度下降）, paused=暂停, deleted=已删除"
    },
    "weight": {
      "type": "number",
      "minimum": 0,
      "description": "规则权重",
      "examples": [1.0, 0.5]
    },
    "human_labeled": {
      "type": "boolean",
      "description": "是否人工标记",
      "default": false
    },
    "label_comment": {
      "type": "string",
      "description": "人工标记备注"
    },
    "applied_count": {
      "type": "integer",
      "minimum": 0,
      "description": "规则被应用次数"
    },
    "success_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "规则应用成功率"
    }
  }
}
```

**示例 JSON：**

```json
{
  "rule_id": "RUL-2026-000001",
  "preference_type": "content",
  "rule_content": "用户偏好以数字/数据开头的标题风格，此类内容点击率平均高出35%",
  "confidence": 87,
  "sources": ["performance_data", "review_history"],
  "created_at": "2026-07-10T10:00:00+08:00",
  "last_updated_at": "2026-07-12T18:00:00+08:00",
  "status": "active",
  "weight": 1.0,
  "human_labeled": true,
  "label_comment": "运营经理确认，长期观察成立",
  "applied_count": 45,
  "success_rate": 0.82
}
```

---

#### 4.6.2 LearningRecord（学习记录）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/learning_record.json",
  "title": "LearningRecord",
  "description": "学习记录 — 用于 M-25 → M-26 传递学习数据",
  "type": "object",
  "required": ["record_id", "content_id", "event_type", "event_data", "recorded_at"],
  "properties": {
    "record_id": {
      "type": "string",
      "pattern": "^LRN-\\d{4}-\\d{6}$",
      "description": "学习记录ID",
      "examples": ["LRN-2026-000001"]
    },
    "content_id": {
      "type": "string",
      "pattern": "^CTN-\\d{4}-\\d{6}$",
      "description": "关联内容ID"
    },
    "review_task_id": {
      "type": "string",
      "pattern": "^REV-\\d{4}-\\d{6}$",
      "description": "关联审阅任务ID"
    },
    "event_type": {
      "type": "string",
      "enum": ["revision_applied", "revision_ignored", "auto_pass", "manual_review", "review_outcome", "performance_feedback"],
      "description": "学习事件类型"
    },
    "event_data": {
      "type": "object",
      "description": "事件详细数据（结构依 event_type 而定）",
      "examples": [{
        "original_text": "...",
        "revised_text": "...",
        "revision_type": "must_fix",
        "accepted": true
      }]
    },
    "recorded_at": {
      "type": "string",
      "format": "date-time",
      "examples": ["2026-07-12T16:30:00+08:00"]
    }
  }
}
```

**示例 JSON：**

```json
{
  "record_id": "LRN-2026-000001",
  "content_id": "CTN-2026-000001",
  "review_task_id": "REV-2026-000001",
  "event_type": "revision_applied",
  "event_data": {
    "original_text": "这个产品非常牛逼",
    "revised_text": "这个产品性能卓越",
    "revision_type": "must_fix",
    "revision_reason": "敏感词替换",
    "accepted": true
  },
  "recorded_at": "2026-07-12T16:30:00+08:00"
}
```

---

### 4.7 报告域（Report Domain）

#### 4.7.1 LearningReport（学习报告）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/learning_report.json",
  "title": "LearningReport",
  "description": "学习报告 — 用于 M-30 输出学习成效量化报告",
  "type": "object",
  "required": ["report_id", "period", "generated_at"],
  "properties": {
    "report_id": {
      "type": "string",
      "pattern": "^RPT-\\d{4}-\\d{6}$",
      "description": "报告ID",
      "examples": ["RPT-2026-000050"]
    },
    "period": {
      "type": "object",
      "required": ["start", "end"],
      "properties": {
        "start": {
          "type": "string",
          "format": "date",
          "examples": ["2026-07-06"]
        },
        "end": {
          "type": "string",
          "format": "date",
          "examples": ["2026-07-12"]
        }
      }
    },
    "manual_revision_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "人工修改率（需要修改的内容占比）"
    },
    "first_pass_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "一次通过率（首次审阅即通过的内容占比）"
    },
    "avg_review_duration": {
      "type": "number",
      "minimum": 0,
      "description": "平均审阅耗时（分钟）"
    },
    "auto_pass_rate": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "系统自动通过率（无需人工审阅直接发布的内容占比）"
    },
    "new_rules_count": {
      "type": "integer",
      "minimum": 0,
      "description": "新增规则数"
    },
    "top10_confidence": {
      "type": "array",
      "description": "置信度最高的10条规则",
      "maxItems": 10,
      "items": {
        "type": "object",
        "required": ["rule_id", "rule_content", "confidence"],
        "properties": {
          "rule_id": { "type": "string", "pattern": "^RUL-\\d{4}-\\d{6}$" },
          "rule_content": { "type": "string" },
          "confidence": { "type": "integer", "minimum": 0, "maximum": 100 }
        }
      }
    },
    "new_preferences": {
      "type": "array",
      "description": "新增偏好特征列表",
      "items": {
        "type": "object",
        "required": ["feature", "type", "confidence"],
        "properties": {
          "feature": {
            "type": "string",
            "description": "偏好特征描述"
          },
          "type": {
            "type": "string",
            "enum": ["content", "visual", "strategy"],
            "description": "偏好类型"
          },
          "confidence": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "置信度"
          },
          "supporting_evidence": {
            "type": "string",
            "description": "支撑证据"
          }
        }
      }
    },
    "anomalies": {
      "type": "array",
      "description": "异常项列表",
      "items": {
        "type": "object",
        "required": ["type", "description", "severity"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["confidence_drop", "rule_conflict", "performance_decline", "data_gap", "model_drift"],
            "description": "异常类型"
          },
          "description": {
            "type": "string",
            "description": "异常描述"
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "warning", "info"],
            "description": "严重程度"
          },
          "affected_rules": {
            "type": "array",
            "description": "受影响的规则ID",
            "items": {
              "type": "string",
              "pattern": "^RUL-\\d{4}-\\d{6}$"
            }
          },
          "suggestion": {
            "type": "string",
            "description": "处理建议"
          }
        }
      }
    },
    "generated_at": {
      "type": "string",
      "format": "date-time",
      "examples": ["2026-07-13T09:00:00+08:00"]
    }
  }
}
```

**示例 JSON：**

```json
{
  "report_id": "RPT-2026-000050",
  "period": {
    "start": "2026-07-06",
    "end": "2026-07-12"
  },
  "manual_revision_rate": 0.28,
  "first_pass_rate": 0.64,
  "avg_review_duration": 18.5,
  "auto_pass_rate": 0.12,
  "new_rules_count": 7,
  "top10_confidence": [
    {
      "rule_id": "RUL-2026-000001",
      "rule_content": "用户偏好以数字/数据开头的标题风格",
      "confidence": 87
    },
    {
      "rule_id": "RUL-2026-000003",
      "rule_content": "视频前3秒出现人物面部可提升完播率",
      "confidence": 83
    }
  ],
  "new_preferences": [
    {
      "feature": "用户对'AI+行业应用'类话题的互动率比纯技术科普高2.3倍",
      "type": "content",
      "confidence": 78,
      "supporting_evidence": "基于最近30条内容的A/B对比分析"
    }
  ],
  "anomalies": [
    {
      "type": "confidence_drop",
      "description": "规则 RUL-2026-000015 置信度从82%降至54%，可能已过时",
      "severity": "warning",
      "affected_rules": ["RUL-2026-000015"],
      "suggestion": "建议人工复核该规则是否仍适用，或标记为 degraded 状态"
    }
  ],
  "generated_at": "2026-07-13T09:00:00+08:00"
}
```

---

## 5. 模块间关键接口对接表

| 序号 | 上游模块 | 下游模块 | 传递数据 | 数据格式引用 | 触发条件 |
|---|---|---|---|---|---|
| 1 | M-01 关键词智能扩展 | M-02 图文素材采集 | 扩展关键词列表 | [Keyword](#412-keyword关键词对象) | 选题计划确认后 |
| 2 | M-06 素材入库与版权追踪 | M-07 素材匹配与调用 | 素材ID列表 | [Material](#411-material素材对象) | 素材入库完成 |
| 3 | M-07 素材匹配与调用 | M-08 文案差异化生成 | 素材+选题信息 | [Content](#421-content内容对象)（partial） | 素材匹配完成 |
| 4 | M-08 文案差异化生成 | M-11 内容精加工与定稿 | 文案草稿 | [Content](#421-content内容对象) | 文案生成完成 |
| 5 | M-12 合规性自检 | M-11 内容精加工与定稿 | 合规报告 | [ComplianceResult](#422-complianceresult合规检查结果) | 合规检查完成 |
| 6 | M-11 内容精加工与定稿 | M-13 分级审阅引擎 | 待审内容 | [ReviewTask](#431-reviewtask审阅任务) | 内容定稿完成 |
| 7 | M-13 分级审阅引擎 | M-16 多平台分发 | 审阅通过内容 | [Content](#421-content内容对象) | 审阅通过 |
| 8 | M-16 多平台分发 | M-17 发布状态监控与应急响应 | 发布任务 | [PublishTask](#441-publishtask发布任务) | 分发执行 |
| 9 | M-18 效果数据采集 | M-20 数据清洗与聚合 | 效果数据 | [PerformanceData](#442-performancedata效果数据) | 采集节点到达 |
| 10 | M-20/M-21/M-22/M-23 | M-24 下期计划草案生成 | 综合分析数据 | [AnalyticsReport](#451-analyticsreport分析报告) | 分析周期结束 |
| 11 | M-25 学习数据收集 | M-26 偏好提炼与规则生成 | 学习记录 | [LearningRecord](#462-learningrecord学习记录) | 审阅/发布事件发生 |

---

## 6. 状态流转定义

### 6.1 内容生命周期状态机

```
draft ──────────────► compliance_checking
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
    compliance_passed  compliance_failed ──► draft (返修)
              │
              ▼
       pending_review
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
review_   review_   in_review
approved  rejected
    │         │
    │         └──► draft (返修)
    ▼
ready_to_publish
    │
    ▼
 published
```

### 6.2 发布任务状态机

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

### 6.3 审阅任务状态机

```
pending_review ──► in_review
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      approved   rejected   needs_revision
                      │           │
                      │           └──► pending_review (重新提交)
                      ▼
                  (closed)
```

---

## 7. 附录

### 7.1 平台枚举值对照表

| 平台中文名 | 枚举值 | API标识 |
|---|---|---|
| 抖音 | `douyin` | douyin |
| 小红书 | `xiaohongshu` | xiaohongshu |
| B站 | `bilibili` | bilibili |
| X（Twitter） | `twitter` | twitter |

### 7.2 公共错误响应格式

当模块间调用失败时，下游模块应返回统一的错误格式：

```json
{
  "error": {
    "code": "INVALID_MATERIAL_ID",
    "message": "素材ID格式不正确",
    "details": {
      "field": "material_id",
      "value": "INVALID-001",
      "expected_pattern": "^MAT-\\d{4}-\\d{6}$"
    },
    "timestamp": "2026-07-12T10:30:00+08:00",
    "request_id": "REQ-2026-000001"
  }
}
```

### 7.3 分页参数约定

涉及列表查询的接口统一使用以下分页参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `page` | integer | 1 | 页码（从1开始） |
| `page_size` | integer | 20 | 每页条数（最大100） |
| `total` | integer | - | 总条数（响应中包含） |

分页响应格式：

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### 7.4 版本历史

| 版本 | 日期 | 变更说明 |
|---|---|---|
| v1.0 | 2026-07-12 | 初始版本，定义全部7个域的JSON Schema和模块间接口契约 |

---

> **使用须知**：本文档为 Hermes 系统模块间数据格式的唯一权威来源。所有模块开发、接口对接和集成测试必须严格遵循本文档定义的数据格式。如有格式变更需求，需先更新本文档并经架构评审通过后方可实施。
