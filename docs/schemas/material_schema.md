# 素材域 JSON Schema 定义

> 本文件集中定义素材域（Material Domain）相关的所有 JSON Schema，包括 Material 和 Keyword 两个核心对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. Material（素材对象）

### 1.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/material.json",
  "title": "Material",
  "description": "素材对象 — 用于模块 M-02、M-03、M-06、M-07、M-15 之间传递素材数据",
  "type": "object",
  "required": [
    "material_id",
    "type",
    "path",
    "copyright_status",
    "resolution",
    "file_size",
    "clarity_score",
    "collected_at"
  ],
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

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `material_id` | string | 是 | 素材唯一标识，格式 MAT-YYYY-NNNNNN |
| `topic_id` | string | 否 | 关联的选题计划编号 |
| `type` | string | 是 | 素材类型：image / video / audio / text |
| `path` | string | 是 | 素材在存储系统中的路径 |
| `tags` | string[] | 否 | 素材标签，用于分类和检索 |
| `copyright_status` | string | 是 | 版权状态，决定素材是否可商用 |
| `resolution` | object | 是 | 素材分辨率（宽×高） |
| `file_size` | integer | 是 | 文件大小（字节） |
| `clarity_score` | integer | 是 | 清晰度评分（0-100） |
| `source_url` | string | 否 | 素材原始来源 URL |
| `collected_at` | string | 是 | 采集时间（ISO 8601） |
| `license_expiry` | string | 否 | 授权到期日 |
| `platform` | string | 否 | 采集来源平台 |
| `duration` | number | 否 | 时长（秒），仅音视频类型 |
| `thumbnail_path` | string | 否 | 缩略图存储路径 |

### 1.3 示例

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

### 1.4 版权状态枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `free` | 免费可商用 | 可自由使用，无需授权 |
| `licensed` | 已授权 | 已获取使用授权 |
| `expiring` | 即将到期 | 授权将在 30 天内到期 |
| `expired` | 已过期 | 授权已过期，不可使用 |
| `unknown` | 未知 | 版权状态不明，需人工确认 |

### 1.5 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-02 图文素材采集 | 生产者 | 创建 Material 对象 |
| M-03 视频素材采集 | 生产者 | 创建 Material 对象 |
| M-05 素材去重与质量控制 | 消费者+生产者 | 读取并更新 clarity_score |
| M-06 素材入库与版权追踪 | 消费者+生产者 | 读取并更新 copyright_status |
| M-07 素材匹配与调用 | 消费者 | 读取并匹配素材 |
| M-15 通用素材池管理 | 消费者 | 读取通用素材 |

---

## 2. Keyword（关键词对象）

### 2.1 Schema 定义

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

### 2.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `original_word` | string | 是 | 用户输入的原始关键词 |
| `expanded_words` | array | 是 | LLM 扩展后的关键词列表 |
| `expanded_words[].word` | string | 是 | 扩展关键词 |
| `expanded_words[].type` | string | 是 | 扩展类型：synonym / related / long_tail |
| `expanded_words[].relevance` | number | 是 | 与原词的关联度（0-1） |
| `platform` | string | 是 | 目标搜索平台 |
| `topic_id` | string | 否 | 关联选题编号 |
| `created_at` | string | 否 | 生成时间 |

### 2.3 示例

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

### 2.4 扩展类型枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `synonym` | 同义词 | 与原词含义相同的词 |
| `related` | 相关词 | 与原词领域相关的词 |
| `long_tail` | 长尾词 | 更具体的长尾搜索词 |

### 2.5 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-01 关键词智能扩展 | 生产者 | 基于 LLM 生成扩展关键词 |
| M-02 图文素材采集 | 消费者 | 使用扩展关键词搜索素材 |
| M-03 视频素材采集 | 消费者 | 使用扩展关键词搜索素材 |
| M-24 下期计划草案生成 | 间接消费者 | 计划草案中的选题建议可生成新关键词 |

---

## 3. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `materials` | Material | M-02, M-03, M-06, M-07, M-15 |
| `material_tags` | Material.tags | M-06 |
| `copyright_records` | Material.copyright_status | M-06 |
| `keywords` | Keyword | M-01 |
| `topics` | Keyword.topic_id | M-01 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.1 节
