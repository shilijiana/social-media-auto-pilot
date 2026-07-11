# 学习域 JSON Schema 定义

> 本文件集中定义学习域（Learning Domain）相关的所有 JSON Schema，包括 PreferenceRule 和 LearningReport 两个核心对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. PreferenceRule（偏好规则）

### 1.1 Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://hermes.social-auto-pilot/schemas/preference_rule.json",
  "title": "PreferenceRule",
  "description": "偏好规则 — 用于 M-26、M-27、M-29 传递偏好规则数据",
  "type": "object",
  "required": [
    "rule_id",
    "preference_type",
    "rule_content",
    "confidence",
    "sources",
    "created_at",
    "status",
    "weight"
  ],
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

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rule_id` | string | 是 | 规则唯一标识，格式 RUL-YYYY-NNNNNN |
| `preference_type` | string | 是 | 偏好类型：content / visual / strategy |
| `rule_content` | string | 是 | 规则的自然语言描述 |
| `confidence` | integer | 是 | 置信度评分（0-100） |
| `sources` | string[] | 是 | 规则推导来源 |
| `created_at` | string | 是 | 规则创建时间 |
| `last_updated_at` | string | 否 | 最后更新时间 |
| `status` | string | 是 | 规则生命周期状态 |
| `weight` | number | 是 | 规则权重系数 |
| `human_labeled` | boolean | 否 | 是否经过人工确认 |
| `label_comment` | string | 否 | 人工标注备注 |
| `applied_count` | integer | 否 | 规则被应用的累计次数 |
| `success_rate` | number | 否 | 规则应用成功率（0-1） |

### 1.3 示例

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

### 1.4 偏好类型枚举

| 枚举值 | 中文 | 说明 | 示例 |
|--------|------|------|------|
| `content` | 内容偏好 | 关于文案风格、话题方向、标题格式的偏好 | "标题含数字可提升点击率" |
| `visual` | 视觉偏好 | 关于封面设计、色调、构图、字体风格的偏好 | "冷色调封面点击率更高" |
| `strategy` | 策略偏好 | 关于发布时间、频次、平台策略的偏好 | "晚8点发布互动率最高" |

### 1.5 规则状态枚举

| 枚举值 | 中文 | 说明 | 是否生效 |
|--------|------|------|---------|
| `active` | 生效中 | 规则已验证，正在被系统使用 | 是 |
| `degraded` | 降级 | 规则置信度下降，仍可用但权重降低 | 是（降权） |
| `paused` | 暂停 | 规则暂时停用 | 否 |
| `deleted` | 已删除 | 规则已移除 | 否 |

### 1.6 规则状态机

```
created ──► active ──► degraded ──► deleted
                │          │
                │          └──► active (置信度回升)
                │
                └──► paused ──► active (恢复)
                        │
                        └──► deleted
```

### 1.7 规则来源枚举

| 来源值 | 说明 |
|--------|------|
| `review_history` | 从审阅修改记录中提炼 |
| `performance_data` | 从效果数据中分析得出 |
| `comment_analysis` | 从用户评论情感分析中提取 |
| `competitor_analysis` | 从竞品分析中借鉴 |
| `manual_input` | 人工手动录入 |
| `template_import` | 从模板导入 |

### 1.8 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-26 偏好提炼与规则生成 | 生产者 | 从学习数据中生成新规则 |
| M-27 规则时效性管理 | 消费者+生产者 | 管理规则生命周期，更新状态 |
| M-28 初始偏好模板导入 | 生产者 | 导入预设模板规则 |
| M-29 学习成果应用 | 消费者 | 读取 active 规则并分发到业务模块 |
| M-30 学习成效量化与报告 | 消费者 | 评估规则效果 |

---

## 2. LearningReport（学习报告）

### 2.1 Schema 定义

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

### 2.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `report_id` | string | 是 | 报告唯一标识 |
| `period` | object | 是 | 统计周期 |
| `manual_revision_rate` | number | 否 | 需要人工修改的内容占比 |
| `first_pass_rate` | number | 否 | 首次审阅即通过的内容占比 |
| `avg_review_duration` | number | 否 | 平均审阅耗时（分钟） |
| `auto_pass_rate` | number | 否 | 无需人工审阅直接发布的内容占比 |
| `new_rules_count` | integer | 否 | 本周期新增的规则数量 |
| `top10_confidence` | array | 否 | 置信度最高的 10 条规则 |
| `new_preferences` | array | 否 | 新发现的偏好特征 |
| `anomalies` | array | 否 | 检测到的异常项 |
| `generated_at` | string | 是 | 报告生成时间 |

### 2.3 示例

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

### 2.4 核心评估指标

| 指标 | 计算方式 | 目标值 | 说明 |
|------|---------|--------|------|
| `manual_revision_rate` | 需修改内容数 / 总内容数 | < 20% | 越低说明 AI 生成质量越高 |
| `first_pass_rate` | 一次通过数 / 总提交数 | > 70% | 越高说明内容质量越稳定 |
| `auto_pass_rate` | 自动通过数 / 总内容数 | > 40% | 越高说明系统信任度越高 |
| `avg_review_duration` | 总审阅耗时 / 审阅次数 | < 15min | 越低说明审阅效率越高 |
| `new_rules_count` | 本周期新增规则数 | 持续增长 | 反映学习活跃度 |

### 2.5 异常类型枚举

| 枚举值 | 中文 | 说明 | 建议处理 |
|--------|------|------|---------|
| `confidence_drop` | 置信度骤降 | 某条规则的置信度快速下降 | 人工复核规则有效性 |
| `rule_conflict` | 规则冲突 | 两条规则存在矛盾 | 人工裁定优先级 |
| `performance_decline` | 效果下降 | 应用规则后整体效果反而下降 | 暂停相关规则 |
| `data_gap` | 数据不足 | 某些维度缺乏足够数据支撑 | 延长采集周期 |
| `model_drift` | 偏好偏移 | 用户偏好发生整体性变化 | 重置规则库 |

### 2.6 严重程度枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `critical` | 严重 | 需立即处理，否则影响系统运行 |
| `warning` | 警告 | 需要关注，建议在下一周期处理 |
| `info` | 信息 | 一般性提示，不影响正常运行 |

### 2.7 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-30 学习成效量化与报告 | 生产者 | 综合分析并生成 LearningReport |
| M-29 学习成果应用 | 间接消费者 | 根据报告异常调整规则分发策略 |

---

## 3. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `learning_records` | (独立 Schema) | M-25 |
| `preference_rules` | PreferenceRule | M-26, M-27, M-29 |
| `preference_templates` | PreferenceRule (模板) | M-28 |
| `learning_reports` | LearningReport | M-30 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.6-4.7 节
