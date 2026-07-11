# FLOW_01: 素材采集闭环

> 闭环路径: M-01 → M-02/M-03 → M-04 → M-05 → M-06
> 闭环目标: 从外部数据源采集原始素材，经清洗、分类、打标后入库，并生成采集任务报告
> 目标读者: Hermes Agent

---

## 1. ASCII 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        素材采集闭环 (Material Ingestion Loop)                  │
│                                                                             │
│   ┌──────────┐      ┌──────────────┐      ┌──────────────┐                 │
│   │  M-01    │      │   M-02       │      │   M-04       │                 │
│   │ 数据源   │─────▶│  素材抓取    │─────▶│  素材清洗    │                 │
│   │ 配置     │      │  (Ingest)    │      │  (Cleanse)   │                 │
│   │          │      └──────┬───────┘      └──────┬───────┘                 │
│   │ 定义:    │             │                     │                          │
│   │ - 来源URL│             │ 原始素材            │ 清洗后素材                │
│   │ - 爬取频率│            │ {raw_json}          │ {clean_struct}           │
│   │ - 过滤规则│            │                     │                          │
│   └──────────┘             │                     │                          │
│                            ▼                     │                          │
│                     ┌──────────────┐             │                          │
│                     │   M-03       │             │                          │
│                     │  手工上传    │             │                          │
│                     │  (Upload)    │             │                          │
│                     │              │             │                          │
│                     │ 用户手动     │             │                          │
│                     │ 提交素材文件  │             │                          │
│                     └──────┬───────┘             │                          │
│                            │                     │                          │
│                            └──────────┬──────────┘                          │
│                                       ▼                                     │
│                              ┌──────────────────┐                           │
│                              │     M-05         │                           │
│                              │   素材分类/打标   │                           │
│                              │   (Classify)     │                           │
│                              │                  │                           │
│                              │ 输入: 清洗后素材  │                           │
│                              │ 输出: 带标签素材  │                           │
│                              │ {tagged_asset}    │                           │
│                              └────────┬─────────┘                           │
│                                       │                                     │
│                                       ▼                                     │
│                              ┌──────────────────┐                           │
│                              │     M-06         │                           │
│                              │   素材入库 + 报告 │                           │
│                              │   (Ingest Report) │                           │
│                              │                  │                           │
│                              │ 持久化到素材库    │                           │
│                              │ 生成采集摘要报告  │                           │
│                              │ → 触发 M-07      │                           │
│                              └──────────────────┘                           │
│                                                                             │
│   闭环终点: 素材就绪信号 (asset_ready) → 内容生产闭环 (FLOW_02)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 各模块角色说明

### M-01 — 数据源配置 (DataSource Config)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环入口，定义素材从哪里来 |
| **输入** | 管理员配置的数据源描述（RSS 地址、API endpoint、爬取站点列表） |
| **输出** | `DataSourceConfig` 结构化配置对象 |
| **关键字段** | `source_url`, `crawl_interval`, `filter_rules`, `auth_token`, `content_type_filter` |

**配置示例:**
```json
{
  "source_id": "src_weibo_hot_001",
  "source_type": "social_media",
  "source_url": "https://api.weibo.com/2/statuses/public_timeline.json",
  "crawl_interval": "PT15M",
  "filter_rules": {
    "min_engagement": 100,
    "allowed_content_types": ["image", "video", "text"],
    "keyword_blacklist": ["广告", "推广"]
  },
  "auth_token": "encrypted_token_xxxxx"
}
```

### M-02 — 素材抓取 (Material Ingest)

| 属性 | 说明 |
|------|------|
| **角色** | 自动爬取/拉取原始素材 |
| **输入** | M-01 的 `DataSourceConfig` |
| **输出** | 原始素材列表 `RawMaterial[]` |
| **关键逻辑** | 定时调度爬取，处理反爬策略，HTTP 重试 |

**输出示例 (raw_json):**
```json
{
  "ingest_batch_id": "ing_20260712_001",
  "source_id": "src_weibo_hot_001",
  "fetched_at": "2026-07-12T10:30:00Z",
  "items": [
    {
      "raw_id": "raw_abc123",
      "source_url": "https://weibo.com/xxxxx/status/12345",
      "content_type": "image",
      "raw_content": "{\"text\":\"今日穿搭分享 #OOTD\",\"images\":[\"https://img.weibo.com/xxxxx.jpg\"]}",
      "meta": {
        "author": "user_123",
        "publish_time": "2026-07-12T09:00:00Z",
        "engagement": {"likes": 2340, "reposts": 567, "comments": 89}
      }
    }
  ],
  "stats": {"total_fetched": 1, "skipped": 0, "errors": 0}
}
```

### M-03 — 手工上传 (Manual Upload)

| 属性 | 说明 |
|------|------|
| **角色** | 补充通道，允许用户直接上传素材文件 |
| **输入** | 用户上传的文件 (jpg/png/mp4/gif/txt) + 元数据 |
| **输出** | 与 M-02 相同格式的 `RawMaterial[]` |
| **区别** | 不需要 `DataSourceConfig`，由用户提供描述性元数据 |

**上传接口:**
```
POST /api/v1/materials/upload
Content-Type: multipart/form-data

Fields:
  file: <binary>
  metadata: { "title": "...", "tags": [...], "source_desc": "..." }
```

### M-04 — 素材清洗 (Material Cleanse)

| 属性 | 说明 |
|------|------|
| **角色** | 对原始素材做标准化处理 |
| **输入** | M-02 或 M-03 的 `RawMaterial[]` |
| **输出** | `CleansedMaterial[]` |
| **处理步骤** | 去重、格式归一化、敏感内容过滤、尺寸/分辨率检查 |

**清洗前 vs 清洗后:**
```
[清洗前 RawMaterial]
  - 重复内容 (同一图片不同 URL)
  - 含敏感词的文本
  - 分辨率 < 720p 的视频
  - 空内容占位符

[清洗后 CleansedMaterial]
  - 去重后保留唯一副本
  - 敏感内容标记为 rejected
  - 低分辨率标记为 low_quality，但仍保留
  - 空内容直接丢弃
```

**输出示例:**
```json
{
  "cleanse_batch_id": "cln_20260712_001",
  "results": [
    {
      "raw_id": "raw_abc123",
      "status": "accepted",
      "cleansed_data": {
        "title": "今日穿搭分享",
        "media_urls": ["https://cdn.internal/materials/img_001.jpg"],
        "text_content": "今日穿搭分享 #OOTD",
        "checksum": "sha256:abc123def456..."
      },
      "quality_score": 0.85
    },
    {
      "raw_id": "raw_def456",
      "status": "rejected",
      "reject_reason": "sensitive_content_detected"
    }
  ],
  "stats": {"total": 2, "accepted": 1, "rejected": 1}
}
```

### M-05 — 素材分类/打标 (Classify & Tag)

| 属性 | 说明 |
|------|------|
| **角色** | 对清洗后的素材做智能分类和标签生成 |
| **输入** | M-04 的 `CleansedMaterial[]` (仅 status=accepted) |
| **输出** | `TaggedAsset[]` |
| **分类维度** | 内容类型 (穿搭/美食/旅行/科技/...)、情感倾向、适用平台 |

**打标输出示例:**
```json
{
  "asset_id": "ast_20260712_001",
  "raw_id": "raw_abc123",
  "tags": {
    "category": "时尚穿搭",
    "sub_category": "夏季日常",
    "sentiment": "positive",
    "style": "casual",
    "elements": ["T恤", "牛仔裤", "帆布鞋"],
    "suitable_platforms": ["小红书", "微博", "抖音"],
    "target_audience": ["18-25岁女性", "穿搭爱好者"]
  },
  "auto_generated_title": "夏日清爽穿搭 | OOTD分享",
  "confidence": 0.92,
  "classified_at": "2026-07-12T10:31:00Z"
}
```

### M-06 — 素材入库 + 采集报告 (Ingest Report)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环收尾，持久化素材并产出采集摘要 |
| **输入** | M-05 的 `TaggedAsset[]` |
| **输出** | `IngestReport` + 数据库写入 + `asset_ready` 事件 |

**报告示例:**
```json
{
  "report_id": "rpt_ing_20260712_001",
  "batch_id": "ing_20260712_001",
  "generated_at": "2026-07-12T10:32:00Z",
  "summary": {
    "total_fetched": 50,
    "after_cleanse": 42,
    "after_tagging": 42,
    "rejected": 8,
    "new_assets": 35,
    "duplicates": 7
  },
  "category_distribution": {
    "时尚穿搭": 12,
    "美食": 8,
    "旅行": 10,
    "科技": 5,
    "其他": 7
  },
  "asset_ids": ["ast_20260712_001", "ast_20260712_002", "..."],
  "next_trigger": "asset_ready → M-07 (素材筛选)"
}
```

---

## 3. 关键数据转换节点

```
M-01 配置对象 ──[调度器]──▶ M-02 原始素材 ──┐
                                            ├──▶ M-04 清洗 ──▶ M-05 打标 ──▶ M-06 入库
M-03 用户上传 ──────────────────────────────┘

转换链:
  DataSourceConfig → RawMaterial → CleansedMaterial → TaggedAsset → DB Record + Report
```

| 节点 | 数据形态 | 关键字段变化 |
|------|---------|-------------|
| M-01→M-02 | 配置 → 原始数据 | 增加 `ingest_batch_id`, `fetched_at`, `raw_content` |
| M-02→M-04 | 原始 → 清洗后 | 增加 `status`(accepted/rejected), `quality_score`, `checksum` |
| M-04→M-05 | 清洗 → 打标 | 增加 `tags`, `auto_generated_title`, `confidence` |
| M-05→M-06 | 打标 → 入库 | 增加 `asset_id`(持久化ID), `report_id` |

---

## 4. 模块间接口连接点

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  M-01   │     │  M-02   │     │  M-04   │     │  M-05   │     │  M-06   │
│         │────▶│         │────▶│         │────▶│         │────▶│         │
│ Config  │ API │ Ingest  │Queue│Cleanse  │Queue│Classify │Queue│ Store   │
│ Service │     │ Worker  │     │ Worker  │     │ Worker  │     │ +Report │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
                      ▲
              ┌───────┘
              │  M-03  │
              │ Upload │
              │  API   │
              └────────┘

接口规格:
  M-01 → M-02: REST POST /api/v1/ingest/trigger  {source_id, config}
  M-03 → M-02: REST POST /api/v1/materials/upload {file, metadata}
  M-02 → M-04: 消息队列 topic: "material.raw.ingested"
  M-04 → M-05: 消息队列 topic: "material.cleansed"
  M-05 → M-06: 消息队列 topic: "material.tagged"
  M-06 → M-07: 事件总线 event: "asset_ready" (桥接 FLOW_02)
```

---

## 5. 调试顺序

调试时按以下顺序逐模块验证:

```
Step 1: M-01 数据源配置
  ├── 验证: 配置文件合法性校验
  ├── 检查: source_url 可达性
  └── 日志关键词: [DataSourceConfig] loaded, source_id=xxx

Step 2: M-02 素材抓取
  ├── 验证: 单次拉取能否返回有效数据
  ├── 检查: HTTP 状态码, 响应体格式
  └── 日志关键词: [IngestWorker] batch_id=xxx, fetched=N items

Step 3: M-03 手工上传
  ├── 验证: 文件上传接口 200 响应
  ├── 检查: 文件大小限制, 格式校验
  └── 日志关键词: [UploadAPI] file received, size=N

Step 4: M-04 素材清洗
  ├── 验证: 重复内容能否被正确去重
  ├── 检查: 敏感词过滤是否生效
  └── 日志关键词: [CleanseWorker] accepted=N, rejected=N

Step 5: M-05 素材打标
  ├── 验证: 分类模型输出是否合理
  ├── 检查: confidence 阈值 (>0.6)
  └── 日志关键词: [ClassifyWorker] asset_id=xxx, tags={...}

Step 6: M-06 入库 + 报告
  ├── 验证: 数据库写入成功
  ├── 检查: report 字段完整性
  └── 日志关键词: [IngestReport] report_id=xxx, new_assets=N

端到端 (E2E):
  ├── 从 M-01 配置触发到 M-06 报告生成
  ├── 验证 asset_ready 事件是否发布
  └── 检查 素材库中可查询到新资产
```

---

## 6. 验收标准

| 编号 | 验收项 | 标准 | 验证方式 |
|------|--------|------|---------|
| AC-01 | 配置驱动抓取 | 修改 M-01 配置后，下一次定时任务使用新配置 | 单元测试 + 集成测试 |
| AC-02 | 素材完整性 | M-02 返回的素材包含所有必填字段 (raw_id, source_url, content_type) | Schema 校验 |
| AC-03 | 上传通道 | M-03 支持 jpg/png/mp4/gif/txt 五种格式，单文件 ≤ 50MB | 接口测试 |
| AC-04 | 去重准确性 | M-04 相同 checksum 的素材去重率 100% | 构造重复数据测试 |
| AC-05 | 敏感内容拦截 | M-04 命中敏感词库的素材标记为 rejected，不进入下游 | 测试用例覆盖 |
| AC-06 | 分类准确率 | M-05 自动分类的 Top-1 准确率 ≥ 85% | 人工标注测试集 |
| AC-07 | 标签完整性 | M-05 输出的 tags 至少包含 category, sentiment, suitable_platforms | 字段存在性检查 |
| AC-08 | 数据持久化 | M-06 所有 accepted 素材写入数据库，asset_id 唯一 | 数据库查询 |
| AC-09 | 报告生成 | M-06 每批次生成一份 report，包含 summary 和 category_distribution | JSON Schema 校验 |
| AC-10 | 闭环触发 | M-06 完成时发布 `asset_ready` 事件，FLOW_02 的 M-07 可消费 | 事件总线监控 |
| AC-11 | 端到端延迟 | 从 M-02 抓取到 M-06 入库完成 ≤ 30 秒 (单批次 100 条) | 性能测试 |
| AC-12 | 错误恢复 | 任一模组异常不影响已处理数据，支持断点续跑 | 故障注入测试 |
