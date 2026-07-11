# M-99: 图片滤镜自动选择模块

> **状态**: 已实现  
> **所属大类**: 素材采集  
> **优先级**: P1  
> **源代码路径**: `src/services/material_collection/image_filter_selector.py`

---

## 1. 模块定位

### 1.1 在闭环中的位置

```
┌─────────────────────────────────────────────────────────────────┐
│                    社交媒体自动化运营闭环                         │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 素材采集  │───>│ 内容生产  │───>│ 审阅管理  │───>│ 分发采集  │  │
│  │          │    │          │    │          │    │          │  │
│  │ M-01     │    │ M-10     │    │ M-15     │    │ M-20     │  │
│  │ M-02     │    │ M-11     │    │ M-16     │    │ M-21     │  │
│  │ M-03     │    │ M-12     │    │          │    │          │  │
│  │ [M-99] ──┤    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                                                  │     │
│       │         ┌──────────┐    ┌──────────┐             │     │
│       └────────>│ 自学习    │<───│ 数据分析  │<────────────┘     │
│                 │ M-25     │    │ M-22     │                    │
│                 └──────────┘    └──────────┘                    │
└─────────────────────────────────────────────────────────────────┘

M-99 位置说明:
  上游: M-02 (图片采集模块) → 传入原始图片列表
  下游: M-10 (内容组装模块) → 使用滤镜处理后的图片
  自学习: M-25 收集用户对滤镜效果的反馈数据
```

### 1.2 核心职责

根据素材内容语义、目标平台特征和用户历史偏好，自动为原始图片选择最佳滤镜方案。输出包含滤镜参数配置和处理后的图片，确保素材视觉风格与平台调性一致。

### 1.3 触发时机

- **自动触发**: M-02（图片采集模块）完成后，由流水线引擎自动调用
- **人工触发**: 运营人员在素材管理后台手动对单张/批量图片执行「重新匹配滤镜」
- **定时触发**: 每周一 02:00 UTC 执行全量素材库滤镜重评估（配合 M-25 偏好更新）

---

## 2. 输入接口 (Input)

### 2.1 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_id", "images", "target_platforms"],
  "properties": {
    "task_id": {
      "type": "string",
      "description": "任务唯一标识，用于追踪和日志关联",
      "pattern": "^task-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    },
    "images": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "items": {
        "type": "object",
        "required": ["image_id", "storage_path", "content_tags"],
        "properties": {
          "image_id": {
            "type": "string",
            "description": "图片唯一 ID，与素材库关联"
          },
          "storage_path": {
            "type": "string",
            "description": "OSS 或本地存储中的图片路径",
            "pattern": "^s3://materials/images/.+\\.(jpg|png|webp)$"
          },
          "content_tags": {
            "type": "array",
            "description": "M-02 产出的内容标签列表",
            "items": {
              "type": "object",
              "properties": {
                "tag": { "type": "string" },
                "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
              }
            }
          },
          "original_source": {
            "type": "string",
            "description": "图片来源 URL 或来源平台",
            "format": "uri"
          }
        }
      }
    },
    "target_platforms": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "enum": ["douyin", "xiaohongshu", "bilibili", "twitter", "instagram", "youtube"]
      }
    },
    "style_preference_id": {
      "type": "string",
      "description": "用户偏好库中的风格 ID，M-25 提供。为空时使用默认模板"
    },
    "batch_options": {
      "type": "object",
      "properties": {
        "consistency_mode": {
          "type": "string",
          "enum": ["uniform", "diverse"],
          "default": "uniform",
          "description": "uniform: 批次内所有图片使用同一滤镜; diverse: 每张独立选择"
        },
        "max_filter_variants": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10,
          "default": 3,
          "description": "每张图片最多生成多少个滤镜变体供下游选择"
        }
      }
    }
  }
}
```

### 2.2 输入示例

```json
{
  "task_id": "task-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "images": [
    {
      "image_id": "img-20250712-001",
      "storage_path": "s3://materials/images/2025/07/12/sunset_beach.jpg",
      "content_tags": [
        { "tag": "自然风景", "confidence": 0.95 },
        { "tag": "日落", "confidence": 0.88 },
        { "tag": "海滩", "confidence": 0.82 },
        { "tag": "暖色调", "confidence": 0.91 }
      ],
      "original_source": "https://unsplash.com/photos/abc123"
    },
    {
      "image_id": "img-20250712-002",
      "storage_path": "s3://materials/images/2025/07/12/coffee_shop.jpg",
      "content_tags": [
        { "tag": "室内场景", "confidence": 0.93 },
        { "tag": "咖啡", "confidence": 0.87 },
        { "tag": "生活方式", "confidence": 0.79 }
      ],
      "original_source": "https://unsplash.com/photos/def456"
    }
  ],
  "target_platforms": ["douyin", "xiaohongshu"],
  "style_preference_id": "style-vintage-warm-01",
  "batch_options": {
    "consistency_mode": "uniform",
    "max_filter_variants": 3
  }
}
```

### 2.3 数据来源

| 字段 | 来源 |
|------|------|
| `task_id` | 流水线引擎生成 |
| `images[].image_id` | 素材库 `materials` 表 |
| `images[].storage_path` | OSS 存储（M-02 上传后返回） |
| `images[].content_tags` | M-02（图片采集模块）输出 |
| `target_platforms` | 分发计划配置 `config/distribution_plan.yaml` |
| `style_preference_id` | M-25（自学习模块）偏好库查询结果 |
| `batch_options` | 流水线引擎根据发布计划注入 |

---

## 3. 输出接口 (Output)

### 3.1 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_id", "status", "results", "execution_metadata"],
  "properties": {
    "task_id": {
      "type": "string",
      "description": "与输入一致的 task_id"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "partial", "failed"],
      "description": "completed: 全部成功; partial: 部分成功; failed: 全部失败"
    },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["image_id", "variants"],
        "properties": {
          "image_id": { "type": "string" },
          "variants": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["variant_id", "filter_name", "filter_params", "output_path", "platform_compatibility"],
              "properties": {
                "variant_id": { "type": "string" },
                "filter_name": { "type": "string" },
                "filter_params": {
                  "type": "object",
                  "properties": {
                    "brightness": { "type": "number", "minimum": -100, "maximum": 100 },
                    "contrast": { "type": "number", "minimum": -100, "maximum": 100 },
                    "saturation": { "type": "number", "minimum": -100, "maximum": 100 },
                    "warmth": { "type": "number", "minimum": -100, "maximum": 100 },
                    "sharpness": { "type": "number", "minimum": 0, "maximum": 100 },
                    "vignette": { "type": "number", "minimum": 0, "maximum": 100 },
                    "grain": { "type": "number", "minimum": 0, "maximum": 100 },
                    "color_overlay": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" }
                  }
                },
                "output_path": { "type": "string" },
                "thumbnail_path": { "type": "string" },
                "platform_compatibility": {
                  "type": "object",
                  "additionalProperties": {
                    "type": "object",
                    "properties": {
                      "score": { "type": "number", "minimum": 0, "maximum": 100 },
                      "warnings": { "type": "array", "items": { "type": "string" } }
                    }
                  }
                },
                "selection_reason": { "type": "string" }
              }
            }
          },
          "error": {
            "type": "object",
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" }
            }
          }
        }
      }
    },
    "execution_metadata": {
      "type": "object",
      "required": ["started_at", "completed_at", "duration_ms", "model_used", "total_images", "success_count", "failed_count"],
      "properties": {
        "started_at": { "type": "string", "format": "date-time" },
        "completed_at": { "type": "string", "format": "date-time" },
        "duration_ms": { "type": "integer" },
        "model_used": { "type": "string" },
        "total_images": { "type": "integer" },
        "success_count": { "type": "integer" },
        "failed_count": { "type": "integer" },
        "filter_templates_used": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

### 3.2 输出示例

```json
{
  "task_id": "task-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "results": [
    {
      "image_id": "img-20250712-001",
      "variants": [
        {
          "variant_id": "var-001-001",
          "filter_name": "vintage-warm-golden",
          "filter_params": {
            "brightness": 5,
            "contrast": 12,
            "saturation": 15,
            "warmth": 25,
            "sharpness": 10,
            "vignette": 20,
            "grain": 8,
            "color_overlay": "#FFD700"
          },
          "output_path": "s3://materials/images/2025/07/12/filtered/sunset_beach_var001.jpg",
          "thumbnail_path": "s3://materials/images/2025/07/12/filtered/sunset_beach_var001_thumb.jpg",
          "platform_compatibility": {
            "douyin": {
              "score": 92,
              "warnings": []
            },
            "xiaohongshu": {
              "score": 88,
              "warnings": ["建议提高亮度 3-5 点以适配小红书首页浅色背景"]
            }
          },
          "selection_reason": "内容标签「日落+暖色调」匹配风格偏好「vintage-warm」，历史数据表明该组合在 douyin 平台互动率 +15%"
        },
        {
          "variant_id": "var-001-002",
          "filter_name": "cinematic-cool",
          "filter_params": {
            "brightness": -5,
            "contrast": 20,
            "saturation": -10,
            "warmth": -10,
            "sharpness": 25,
            "vignette": 35,
            "grain": 15,
            "color_overlay": "#4A90D9"
          },
          "output_path": "s3://materials/images/2025/07/12/filtered/sunset_beach_var002.jpg",
          "thumbnail_path": "s3://materials/images/2025/07/12/filtered/sunset_beach_var002_thumb.jpg",
          "platform_compatibility": {
            "douyin": { "score": 78, "warnings": ["冷色调与内容「日落」语义冲突"] },
            "xiaohongshu": { "score": 72, "warnings": ["小红书用户偏好暖色调"] }
          },
          "selection_reason": "作为对比变体生成，用于 A/B 测试收集用户偏好数据"
        }
      ],
      "error": null
    },
    {
      "image_id": "img-20250712-002",
      "variants": [
        {
          "variant_id": "var-002-001",
          "filter_name": "vintage-warm-coffee",
          "filter_params": {
            "brightness": 8,
            "contrast": 10,
            "saturation": 10,
            "warmth": 30,
            "sharpness": 5,
            "vignette": 25,
            "grain": 12,
            "color_overlay": "#C4956A"
          },
          "output_path": "s3://materials/images/2025/07/12/filtered/coffee_shop_var001.jpg",
          "thumbnail_path": "s3://materials/images/2025/07/12/filtered/coffee_shop_var001_thumb.jpg",
          "platform_compatibility": {
            "douyin": { "score": 90, "warnings": [] },
            "xiaohongshu": { "score": 94, "warnings": [] }
          },
          "selection_reason": "「咖啡+生活方式」标签匹配 vintage-warm 风格，小红书同类内容最高互动率记录"
        }
      ],
      "error": null
    }
  ],
  "execution_metadata": {
    "started_at": "2025-07-12T14:30:00Z",
    "completed_at": "2025-07-12T14:30:12Z",
    "duration_ms": 12345,
    "model_used": "gemini-2.5-flash",
    "total_images": 2,
    "success_count": 2,
    "failed_count": 0,
    "filter_templates_used": ["vintage-warm-golden", "cinematic-cool", "vintage-warm-coffee"]
  }
}
```

### 3.3 数据去向

| 数据项 | 去向 |
|--------|------|
| `results[].variants[].output_path` | OSS 存储 `s3://materials/images/filtered/` |
| `results[].variants[].thumbnail_path` | OSS 存储 `s3://materials/images/filtered/` |
| 完整输出 JSON | 数据库表 `module_outputs`，列 `module_id='M-99'` |
| 滤镜选择记录 | 数据库表 `filter_selections`（供 M-25 学习使用） |
| 下游消费 | M-10（内容组装模块）读取 `module_outputs` 表中 status='completed' 的记录 |

---

## 4. 核心处理逻辑

### 4.1 处理步骤

```
Step 1: 输入校验
  - 做什么: 校验 task_id 格式、images 数组非空且不超过 50 张、target_platforms 合法
  - 怎么判断: 使用 jsonschema 库校验，对比 2.1 中的 Schema
  - 输出: 校验通过 → 进入 Step 2; 校验失败 → 返回 status=failed，记录错误详情

Step 2: 内容语义分析
  - 做什么: 基于 content_tags 和（可选）图片本身进行语义分析，生成图片的「情感向量」
  - 怎么判断: 
      - 优先使用 M-02 产出的 content_tags（置信度 > 0.7 的标签）
      - 若 content_tags 不足（< 3 个高置信度标签），调用 Gemini 视觉模型补充分析
      - 生成情感向量: {warm_cold, bright_dark, natural_artificial, calm_dynamic} 各维度 0-1 值
  - 输出: 每张图片的 `semantic_vector` 对象

Step 3: 偏好库查询
  - 做什么: 如果输入包含 style_preference_id，从偏好库加载风格配置
  - 怎么判断:
      - 调用 M-25 偏好查询接口，传入 style_preference_id 和目标平台
      - 若偏好库命中（置信度 >= 70%），使用偏好库返回的滤镜模板列表
      - 若偏好库未命中或无 style_preference_id，使用 config/filter_rules.yaml 中的默认模板
  - 输出: 滤镜模板列表（含各模板的参数范围）

Step 4: 平台适配调整
  - 做什么: 根据目标平台特征调整滤镜参数
  - 怎么判断:
      - 读取 config/platform_filter_profiles.yaml 中的平台适配规则
      - 对每个目标平台计算适配参数
      - 合并偏好模板参数与平台适配参数（平台适配参数权重 30%，偏好模板权重 70%）
  - 输出: 每个 (图片, 平台) 组合的最终滤镜参数

Step 5: 滤镜应用与渲染
  - 做什么: 调用图像处理引擎应用滤镜
  - 怎么判断:
      - 使用 Pillow 库进行基础滤镜操作（亮度、对比度、饱和度等）
      - 使用 OpenCV 进行高级操作（色调映射、颗粒感、暗角）
      - 每次渲染后检查输出文件大小（超过 10MB 则自动压缩）
      - 生成缩略图（宽 400px，等比缩放，质量 80%）
  - 输出: 处理后的图片文件和缩略图

Step 6: 平台兼容性评分
  - 做什么: 对每个变体评估在各目标平台上的适配得分
  - 怎么判断:
      - 调用 LLM 视觉模型评估滤镜效果与平台调性的匹配度
      - 结合平台规则进行技术检查（分辨率、文件大小、色彩空间等）
      - 得分 = LLM 评分 * 0.6 + 技术合规分 * 0.4
  - 输出: platform_compatibility 对象

Step 7: 结果排序与写入
  - 做什么: 按平台兼容性得分排序变体，写入数据库和存储
  - 怎么判断:
      - 对每张图片的变体按 score 降序排列
      - 保留前 max_filter_variants 个变体
      - 写入 module_outputs 表和 filter_selections 表
      - 写入完成后返回完整输出 JSON
  - 输出: 最终的 Output JSON
```

### 4.2 平台适配

| 平台 | 差异处理 |
|------|---------|
| douyin | 饱和度 +10%，对比度 +8%（竖屏短视频平台需要更鲜艳的视觉效果）；建议输出分辨率 1080x1920 |
| xiaohongshu | 亮度 +5%，锐度 -3%（浅色背景为主，柔和风格更受欢迎）；建议输出分辨率 1080x1440 |
| bilibili | 锐度 +10%，对比度 +5%（横屏长内容，细节展示重要）；支持 16:9 宽高比 |
| twitter | 饱和度 -5%，对比度 +12%（信息流快速浏览，高对比度抓眼球）；输出文件 < 5MB |
| instagram | 颗粒感 +5%，暗角 +10%（平台美学偏好做旧风格）；支持 1:1 和 4:5 比例 |
| youtube | 锐度 +15%，饱和度 +5%（缩略图需在搜索结果中突出）；输出 1280x720 及以上 |

---

## 5. 依赖关系

### 5.1 上游依赖

| 模块 | 依赖内容 | 必须？ |
|------|---------|-------|
| M-02（图片采集模块） | 图片的 `content_tags`、`storage_path`、`original_source` | 是 |
| M-25（自学习模块） | 用户风格偏好 `style_preference_id` 及其关联的滤镜模板列表 | 否 |

### 5.2 下游模块（被谁依赖）

| 模块 | 使用本模块的什么输出 |
|------|-------------------|
| M-10（内容组装模块） | `results[].variants[].output_path` — 滤镜处理后的图片路径 |
| M-10（内容组装模块） | `results[].variants[].filter_name` — 滤镜名称，用于内容描述生成 |
| M-22（数据分析模块） | `execution_metadata` — 滤镜使用频率、耗时统计 |
| M-25（自学习模块） | `filter_selections` 表记录 — 用户最终选择的滤镜变体数据 |

### 5.3 基础设施依赖

| 基础设施 | 用途 |
|---------|------|
| PostgreSQL | 读写表: `module_outputs`（写输出结果）、`filter_selections`（写滤镜选择记录）、`materials`（读图片元数据） |
| Redis | 缓存: 滤镜模板配置（TTL 1h）、平台适配规则（TTL 24h） |
| OSS (S3) | 读路径: `s3://materials/images/`（原始图片）；写路径: `s3://materials/images/filtered/`（处理后图片） |
| LLM (Gemini) | 模型: `gemini-2.5-flash`（内容语义补充分析）；Prompt: `prompts/image_semantic_analysis.md` |
| LLM (Gemini) | 模型: `gemini-2.5-flash`（平台兼容性视觉评估）；Prompt: `prompts/filter_platform_scoring.md` |
| Image Processing | Pillow >= 10.0（基础滤镜操作）；OpenCV >= 4.8（高级图像处理） |

---

## 6. 错误处理策略

| 错误类型 | 处理方式 | 重试策略 | 告警级别 |
|---------|---------|---------|---------|
| 输入 JSON Schema 校验失败 | 返回 status=failed，错误详情写入 `errors` 表，终止执行 | 不重试 | ERROR |
| OSS 图片下载超时（> 30s） | 记录该图片为 failed，继续处理剩余图片 | 3次，指数退避 1s/2s/4s | WARN |
| 图片格式损坏/无法解码 | 记录错误日志，标记该图片为 failed | 不重试 | ERROR |
| LLM 语义分析返回异常（500/429/超时） | 降级：仅使用 M-02 content_tags 进行规则匹配，不使用视觉分析 | 重试 1 次 | WARN |
| LLM 平台评分返回异常 | 降级：使用纯技术规则计算得分（分辨率、文件大小、色彩空间检查） | 重试 1 次 | WARN |
| 滤镜渲染内存溢出（单张 > 500MB） | 自动将图片缩放至最大 4096px 后重试 | 缩放后重试 1 次 | WARN |
| 存储空间不足（OSS 写入失败） | 清理 `s3://materials/images/filtered/tmp/` 临时目录，告警 | 清理后重试 1 次 | CRITICAL |
| 偏好库查询超时（> 5s） | 降级：使用 `config/filter_rules.yaml` 中的默认模板 | 不重试 | WARN |
| 数据库写入失败（连接断开/锁超时） | 暂存结果到本地 JSON 文件，发送告警 | 5次，间隔 2s | CRITICAL |
| 全部图片处理失败（status=failed） | 通知流水线引擎终止下游模块，写入 `pipeline_errors` 表 | 不重试 | CRITICAL |

### 降级策略

当模块完全不可用时（如 LLM 服务中断 + 偏好库不可达 + 平台规则文件损坏），启用以下降级方案：

1. **兜底滤镜**: 使用内置硬编码的「安全滤镜」（亮度 +5、对比度 +5、饱和度 0），确保下游模块可继续运行
2. **人工介入**: 发送企业微信/钉钉通知给运营团队，附上原始图片链接，由人工在后台手动选择滤镜
3. **跳过本模块**: 在 `pipeline_config` 中设置 `image_filter_selector.skip_on_failure = true`，流水线使用原始图片继续后续流程

---

## 7. 自学习触发条件

### 7.1 学习数据收集

本模块向 `filter_selections` 表写入以下数据，供 M-25 定期收集分析：

| 数据字段 | 说明 | 收集时机 |
|---------|------|---------|
| `image_id` | 原始图片 ID | 每次滤镜应用后立即写入 |
| `selected_variant_id` | 用户/流水线最终选择的变体 ID | M-10 确认使用后回写 |
| `filter_name` | 滤镜模板名称 | 每次滤镜应用后立即写入 |
| `content_tags` | 图片内容标签（JSONB） | 每次滤镜应用后立即写入 |
| `platform` | 目标平台 | 每次滤镜应用后立即写入 |
| `compatibility_score` | 平台兼容性得分 | 每次滤镜应用后立即写入 |
| `user_feedback_score` | 用户反馈评分（1-5） | 内容发布后 7 天内，从 M-22 获取互动数据 |
| `ab_test_group` | A/B 测试分组（若使用多个变体） | M-10 选择变体后写入 |

### 7.2 偏好库调用

- **调取偏好类型**: 风格偏好
- **置信度阈值**: >= 70%
- **无偏好时默认行为**: 使用 `config/filter_rules.yaml` 中的 `default_template_set`，基于内容标签进行规则匹配（如「日落→暖色调」「咖啡→柔和对比度」）

### 7.3 阶段演进行为

| 阶段 | 行为差异 |
|------|---------|
| P0 (人工主导) | 滤镜模板完全由运营人员在后台手动选择。模块仅负责应用滤镜和生成缩略图，不参与决策。偏好库为空，LLM 不参与语义分析。 |
| P1 (人机协同) | 模块自动推荐 Top 3 滤镜变体，运营人员从推荐中选择。偏好库开始积累数据。LLM 参与内容语义分析，但不参与最终选择。`max_filter_variants` 建议设为 5。 |
| P2 (系统主导) | 模块自动选择最佳滤镜并直接应用。偏好库置信度 >= 70% 时使用偏好模板，否则使用 LLM 语义匹配。仅当兼容性得分 < 60 时通知人工审核。`max_filter_variants` 建议设为 1-2。 |

---

## 8. 调试检查清单

- [ ] **输入数据是否存在？** 检查 M-02 输出 JSON 中的 images 数组是否非空；检查 OSS 路径 `s3://materials/images/` 下对应文件是否存在
- [ ] **配置文件是否正确？** 检查 `config/filter_rules.yaml` 中的滤镜模板定义、`config/platform_filter_profiles.yaml` 中的平台适配规则、`config/settings.yaml` 中的 OSS/LLM/DB 连接配置
- [ ] **依赖服务可用？** 
  - LLM: `curl -X POST $GEMINI_API_ENDPOINT -H "Authorization: Bearer $GEMINI_API_KEY"` 确认 200 响应
  - OSS: `aws s3 ls s3://materials/images/ --region ap-southeast-1` 确认可访问
  - PostgreSQL: `psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"` 确认连接
  - Redis: `redis-cli -h $REDIS_HOST -p $REDIS_PORT PING` 确认 PONG
- [ ] **图像处理库版本正确？** `python -c "import PIL; print(PIL.__version__)"` 确认 >= 10.0；`python -c "import cv2; print(cv2.__version__)"` 确认 >= 4.8
- [ ] **单模块运行（dry-run 模式）:** `python -m src.services.material_collection.image_filter_selector --dry-run --input tests/fixtures/m99_sample_input.json`
- [ ] **输出 JSON 格式是否匹配 Schema？** 使用 `jsonschema` 库校验: `python -c "from jsonschema import validate; ..."`
- [ ] **数据库写入是否正确？** 查询 `module_outputs` 表: `SELECT * FROM module_outputs WHERE module_id='M-99' AND task_id='<test_task_id>' ORDER BY created_at DESC LIMIT 5;`
- [ ] **文件输出路径是否正确？** `aws s3 ls s3://materials/images/filtered/ --recursive | grep <task_id>`
- [ ] **缩略图是否生成？** 检查 `thumbnail_path` 指向的文件存在且尺寸符合预期（宽 400px）
- [ ] **错误场景降级是否生效？** 模拟 LLM 不可用（临时关闭 API Key），确认模块降级到规则匹配模式
- [ ] **内存使用是否正常？** 批量处理 50 张 4K 图片时，使用 `memory_profiler` 确认内存峰值 < 2GB

---

## 9. Hermes Agent 执行指令

```markdown
## 任务: 调试 M-99 图片滤镜自动选择模块

### 前置条件
1. 确认上游模块 M-02 已完成: 检查 `module_outputs` 表中 M-02 的最新 task_id，状态为 completed
2. 确认基础设施就绪:
   - PostgreSQL 连接: 读取 `config/settings.yaml` → `database` 配置段
   - OSS 存储: 读取 `config/settings.yaml` → `storage.s3` 配置段
   - LLM API: 读取 `config/settings.yaml` → `llm.gemini` 配置段
   - Redis: 读取 `config/settings.yaml` → `redis` 配置段
3. 确认图像处理依赖已安装: 执行 `pip list | grep -E "Pillow|opencv-python"`

### 执行步骤
1. 读取 `config/settings.yaml`，确认以下配置项存在且非空:
   - `database.host`, `database.port`, `database.name`, `database.user`
   - `storage.s3.bucket`, `storage.s3.region`, `storage.s3.access_key`
   - `llm.gemini.api_key`, `llm.gemini.model`
   - `redis.host`, `redis.port`
2. 准备测试数据:
   - 使用 `tests/fixtures/m99_sample_input.json` 作为输入
   - 确认 `tests/fixtures/` 下有测试图片: `test_sunset.jpg`, `test_coffee.jpg`
   - 若测试图片不存在，从 Unsplash 下载两张示例图片并上传到 OSS 测试路径
3. 以 dry-run 模式运行模块:
   ```bash
   python -m src.services.material_collection.image_filter_selector \
     --dry-run \
     --input tests/fixtures/m99_sample_input.json \
     --output tests/fixtures/m99_sample_output.json
   ```
4. 检查输出格式匹配 Schema:
   ```bash
   python -c "
   import json
   from jsonschema import validate, ValidationError
   with open('tests/fixtures/m99_sample_output.json') as f:
       output = json.load(f)
   with open('docs/modules/M-99_image_filter_selector.md') as f:
       # 提取 3.1 节中的 Output JSON Schema 并校验
       pass
   "
   ```
5. 验证数据库写入（非 dry-run 模式时执行）:
   ```sql
   SELECT task_id, status, total_images, success_count, failed_count, duration_ms
   FROM module_outputs
   WHERE module_id = 'M-99'
   ORDER BY created_at DESC
   LIMIT 1;
   ```
6. 验证文件输出路径（非 dry-run 模式时执行）:
   ```bash
   aws s3 ls s3://materials/images/filtered/ --recursive --region ap-southeast-1 | head -20
   ```
7. 检查缩略图尺寸:
   ```bash
   python -c "
   from PIL import Image
   import requests
   # 从 OSS 下载一张缩略图到 /tmp
   img = Image.open('/tmp/test_thumb.jpg')
   assert img.width == 400, f'缩略图宽度应为 400，实际为 {img.width}'
   print(f'缩略图尺寸: {img.width}x{img.height} - OK')
   "
   ```

### 验收标准
- [ ] 输入校验通过: 非法输入（空 images、错误格式 task_id）应返回 status=failed
- [ ] 核心逻辑无异常: dry-run 模式下所有步骤执行无 Python Exception
- [ ] 输出格式匹配 Schema: `jsonschema.validate()` 无 ValidationError
- [ ] 错误场景有降级处理: 模拟 LLM 不可用，确认降级到规则匹配且输出 status=completed
- [ ] 日志输出完整: 检查日志包含 Step 1-7 的执行记录和耗时统计
- [ ] 缩略图生成正确: 宽度 = 400px，宽高比与原图一致
- [ ] 内存使用正常: 处理 50 张 4K 图片时内存峰值 < 2GB

### 注意事项
- dry-run 模式不会写入 OSS 和数据库，仅输出到本地 JSON 文件，适用于开发调试
- 若测试图片不存在，请从 `https://unsplash.com/photos/xxx` 下载到 `tests/fixtures/` 目录
- 首次运行前确保 `config/filter_rules.yaml` 和 `config/platform_filter_profiles.yaml` 已从模板复制:
  ```bash
  cp config/filter_rules.yaml.example config/filter_rules.yaml
  cp config/platform_filter_profiles.yaml.example config/platform_filter_profiles.yaml
  ```
- Gemini API Key 需在 `config/settings.yaml` 或环境变量 `GEMINI_API_KEY` 中配置
- 若遇到 `ModuleNotFoundError: No module named 'cv2'`，执行 `pip install opencv-python-headless>=4.8`
- 批量处理时注意 OSS 并发连接数限制（默认 100），可在 `config/settings.yaml` → `storage.s3.max_concurrency` 中调整
```

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2025-07-01 | v1.0 | 初始版本 — 基础滤镜选择逻辑，支持 6 个平台 | dev-team |
| 2025-07-08 | v1.1 | 新增 A/B 测试变体生成功能；新增缩略图生成 | dev-team |
| 2025-07-10 | v1.2 | 集成 M-25 偏好库查询接口；新增阶段演进行为（P0/P1/P2） | dev-team |
| 2025-07-12 | v1.3 | 新增平台兼容性 LLM 视觉评分；优化批量处理内存使用 | dev-team |
