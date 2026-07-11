# 分析域 JSON Schema 定义

> 本文件集中定义分析域（Analytics Domain）的 JSON Schema，包括 AnalyticsReport 对象。
> 数据格式以 [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 为权威来源。

---

## 1. AnalyticsReport（分析报告）

### 1.1 Schema 定义

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

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `report_id` | string | 是 | 报告唯一标识，格式 RPT-YYYY-NNNNNN |
| `report_type` | string | 是 | 报告类型 |
| `generated_at` | string | 是 | 报告生成时间 |
| `period` | object | 是 | 统计周期 |
| `period.start` | string | 是 | 周期开始日期 |
| `period.end` | string | 是 | 周期结束日期 |
| `metrics_summary` | object | 否 | 关键指标汇总 |
| `horizontal_comparison` | object | 否 | 平台间横向对比 |
| `vertical_comparison` | object | 否 | 时间纵向对比 |
| `hotspot_analysis` | object | 否 | 热点和爆款分析 |
| `suggestions` | array | 否 | 基于分析的改进建议 |

### 1.3 示例

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

### 1.4 报告类型枚举

| 枚举值 | 中文 | 说明 | 生成频率 |
|--------|------|------|---------|
| `daily` | 日报 | 单日数据汇总和分析 | 每日 |
| `weekly` | 周报 | 一周数据汇总，含趋势分析 | 每周 |
| `monthly` | 月报 | 月度数据汇总，含深度分析 | 每月 |
| `per_content` | 单内容分析 | 针对单个内容的详细分析 | 按需 |

### 1.5 建议类别枚举

| 枚举值 | 中文 | 说明 |
|--------|------|------|
| `content` | 内容建议 | 关于选题方向、文案风格的建议 |
| `timing` | 时间建议 | 关于发布时间、频率的建议 |
| `platform` | 平台建议 | 关于平台策略、权重分配的建议 |
| `style` | 风格建议 | 关于视觉风格、剪辑风格的建议 |
| `interaction` | 互动建议 | 关于评论互动、粉丝运营的建议 |

### 1.6 横向对比指标

横向对比 (`horizontal_comparison`) 以平台为 key，每个平台包含以下可选指标：

| 指标 | 说明 |
|------|------|
| `views` | 该平台总播放量/阅读量 |
| `engagement_rate` | 该平台平均互动率 |
| `likes` | 该平台总点赞数 |
| `comments` | 该平台总评论数 |
| `shares` | 该平台总转发数 |
| `favorites` | 该平台总收藏数 |
| `new_followers` | 该平台新增粉丝数 |

### 1.7 纵向对比指标

纵向对比 (`vertical_comparison`) 以指标名为 key，每个指标包含：

| 字段 | 说明 |
|------|------|
| `current` | 当前周期的值 |
| `previous` | 上一周期的值 |
| `change_rate` | 变化率（正数为增长，负数为下降） |

### 1.8 使用模块

| 模块 | 角色 | 操作 |
|------|------|------|
| M-20 数据清洗与聚合 | 生产者 | 生成基础 AnalyticsReport |
| M-21 多维度效果分析 | 生产者+消费者 | 读取并填充分析维度 |
| M-22 评论区语义挖掘 | 生产者 | 填充评论相关分析 |
| M-23 跨平台热点追踪 | 生产者 | 填充热点分析数据 |
| M-24 下期计划草案生成 | 消费者 | 综合消费完整报告生成计划 |
| M-25 学习数据收集 | 消费者 | 收集分析结果用于自学习 |

---

## 2. 关联数据库表

| 表名 | 对应 Schema | 主要模块 |
|------|------------|---------|
| `analytics_reports` | AnalyticsReport | M-20, M-21 |
| `comment_analysis` | (独立 Schema) | M-22 |
| `hot_topics` | AnalyticsReport.hotspot_analysis | M-23 |
| `plan_drafts` | (独立 Schema) | M-24 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **权威来源**: [INTERFACE_CONTRACT.md](../INTERFACE_CONTRACT.md) 第 4.5 节
