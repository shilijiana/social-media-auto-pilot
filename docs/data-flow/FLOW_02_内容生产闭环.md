# FLOW_02: 内容生产闭环

> 闭环路径: M-07 → M-08 → M-09/M-10 → M-11 → M-12
> 闭环目标: 从素材库筛选素材，经内容策划、多平台适配生成、版本管理后产出待审阅内容
> 目标读者: Hermes Agent

---

## 1. ASCII 流程图

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      内容生产闭环 (Content Production Loop)                     │
│                                                                              │
│   ┌──────────┐      ┌──────────────┐      ┌─────────────────────────────┐   │
│   │  M-07    │      │   M-08       │      │   M-09 / M-10               │   │
│   │ 素材筛选 │─────▶│  内容策划    │─────▶│  内容生成 (分平台)          │   │
│   │ (Select) │      │  (Plan)      │      │                             │   │
│   │          │      │              │      │  ┌──────────┐ ┌──────────┐  │   │
│   │ 输入:    │      │ 输入: 素材   │      │  │ M-09     │ │ M-10     │  │   │
│   │ asset_   │      │ 输出: 策划案 │      │  │ 图文内容 │ │ 视频内容 │  │   │
│   │ ready    │      │ {plan}       │      │  │ (Image+  │ │ (Video)  │  │   │
│   │ 事件     │      │              │      │  │  Text)   │ │          │  │   │
│   └──────────┘      └──────┬───────┘      │  └────┬─────┘ └────┬─────┘  │   │
│                            │              │       │            │        │   │
│   素材库查询:              │              │  生成图文帖   生成短视频    │   │
│   - 按时间范围             │              │  (小红书/微博) (抖音/B站)   │   │
│   - 按分类/标签            │              └───────┼────────────┼────────┘   │
│   - 按质量分               │                      │            │            │
│                            │                      └─────┬──────┘            │
│                            │                            ▼                   │
│                            │                     ┌──────────────┐           │
│                            │                     │    M-11      │           │
│                            │                     │  版本管理    │           │
│                            │                     │  (Version)   │           │
│                            │                     │              │           │
│                            │                     │ 多版本迭代:  │           │
│                            │                     │ v1 → v2 → v3 │           │
│                            │                     │ diff 追踪    │           │
│                            │                     └──────┬───────┘           │
│                            │                            │                   │
│                            │                            ▼                   │
│                            │                     ┌──────────────┐           │
│                            │                     │    M-12      │           │
│                            │                     │  内容封装    │           │
│                            │                     │  (Package)   │           │
│                            │                     │              │           │
│                            │                     │ 输出:        │           │
│                            │                     │ ContentPack  │           │
│                            │                     │ → 触发 M-13  │           │
│                            └─────────────────────┴──────────────┘           │
│                                                                              │
│   闭环终点: 待审阅内容包 (content_pack_ready) → 审阅分发闭环 (FLOW_03)         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 各模块角色说明

### M-07 — 素材筛选 (Material Select)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环入口，从素材库中筛选本轮生产所需的素材 |
| **触发** | 监听 `asset_ready` 事件 或 定时调度 (每日 09:00/15:00) |
| **输入** | 素材库查询条件 (时间范围、分类、标签、质量分) |
| **输出** | `SelectedMaterial[]` — 筛选后的素材子集 |

**筛选查询示例:**
```json
{
  "query": {
    "ingested_after": "2026-07-11T00:00:00Z",
    "categories": ["时尚穿搭", "美食"],
    "quality_score_min": 0.7,
    "exclude_used": true,
    "limit": 20,
    "sort_by": "engagement_potential",
    "sort_order": "desc"
  }
}
```

**筛选结果示例:**
```json
{
  "selection_id": "sel_20260712_001",
  "selected_at": "2026-07-12T09:00:00Z",
  "materials": [
    {
      "asset_id": "ast_20260712_001",
      "title": "夏日清爽穿搭 | OOTD分享",
      "category": "时尚穿搭",
      "tags": ["夏季", "casual", "T恤"],
      "quality_score": 0.85,
      "engagement_potential": 0.78
    }
  ],
  "selection_rationale": "基于过去7天高互动率分类的加权采样"
}
```

### M-08 — 内容策划 (Content Plan)

| 属性 | 说明 |
|------|------|
| **角色** | 根据筛选素材制定内容发布计划 |
| **输入** | M-07 的 `SelectedMaterial[]` + 发布日历约束 |
| **输出** | `ContentPlan` — 包含标题、角度、目标平台、发布时间 |

**策划案示例:**
```json
{
  "plan_id": "pln_20260712_001",
  "created_at": "2026-07-12T09:05:00Z",
  "entries": [
    {
      "entry_id": "ent_001",
      "asset_id": "ast_20260712_001",
      "planned_title": "夏天这样穿，回头率翻倍！",
      "angle": "实用穿搭技巧",
      "target_platforms": [
        {
          "platform": "小红书",
          "format": "图文",
          "scheduled_time": "2026-07-13T12:00:00+08:00",
          "tone": "亲切分享"
        },
        {
          "platform": "抖音",
          "format": "短视频",
          "scheduled_time": "2026-07-13T19:00:00+08:00",
          "tone": "潮流炫酷"
        }
      ],
      "priority": "high",
      "content_brief": "用3套夏日搭配展示 casual 风格，突出舒适感和时尚感"
    }
  ]
}
```

### M-09 — 图文内容生成 (Image+Text Generation)

| 属性 | 说明 |
|------|------|
| **角色** | 为图文平台 (小红书/微博/Instagram) 生成帖子内容 |
| **输入** | M-08 中 format=图文 的策划条目 |
| **输出** | `ImageTextContent` — 标题、正文、配图、标签 |

**输出示例:**
```json
{
  "content_id": "cnt_img_20260712_001",
  "plan_entry_id": "ent_001",
  "platform": "小红书",
  "generated_at": "2026-07-12T09:10:00Z",
  "content": {
    "title": "夏天这样穿，回头率翻倍！",
    "body": "姐妹们！今天分享3套超实用的夏日穿搭~\n\nLook 1: 白T + 高腰牛仔裤 + 帆布鞋\n简约又清爽，适合日常通勤\n\nLook 2: 碎花连衣裙 + 草编包\n约会必备！温柔又甜美\n\nLook 3: 运动背心 + 阔腿裤\n街头感十足，显高显瘦\n\n#OOTD #夏日穿搭 #日常穿搭 #时尚分享",
    "images": [
      {
        "url": "https://cdn.internal/generated/img_look1.jpg",
        "alt_text": "白T搭配高腰牛仔裤夏日穿搭",
        "position": 1
      }
    ],
    "hashtags": ["#OOTD", "#夏日穿搭", "#日常穿搭", "#时尚分享"],
    "mention_accounts": [],
    "interactive_elements": {
      "poll": null,
      "question_sticker": "你最喜欢哪套Look？"
    }
  }
}
```

### M-10 — 视频内容生成 (Video Generation)

| 属性 | 说明 |
|------|------|
| **角色** | 为短视频平台 (抖音/B站/YouTube Shorts) 生成视频内容 |
| **输入** | M-08 中 format=视频 的策划条目 |
| **输出** | `VideoContent` — 视频文件、标题、描述、字幕 |

**输出示例:**
```json
{
  "content_id": "cnt_vid_20260712_001",
  "plan_entry_id": "ent_001",
  "platform": "抖音",
  "generated_at": "2026-07-12T09:15:00Z",
  "content": {
    "title": "3套夏日穿搭，回头率200%！",
    "video_url": "https://cdn.internal/generated/vid_look1.mp4",
    "duration_seconds": 28,
    "resolution": "1080x1920",
    "thumbnail_url": "https://cdn.internal/generated/thumb_look1.jpg",
    "subtitles": [
      {"start": 0.0, "end": 2.5, "text": "今天分享3套夏日穿搭"},
      {"start": 2.5, "end": 8.0, "text": "第一套：白T+牛仔裤，清爽简约"}
    ],
    "bgm": {
      "track_id": "bgm_summer_vibe_03",
      "volume": 0.3
    },
    "hashtags": ["#穿搭", "#夏日穿搭", "#OOTD"],
    "description": "3套回头率超高的夏日穿搭！你喜欢哪一套？评论区告诉我~",
    "interactive_elements": {
      "duet_enabled": true,
      "stitch_enabled": true,
      "comment_pin": "大家最喜欢第几套？"
    }
  }
}
```

### M-11 — 版本管理 (Version Management)

| 属性 | 说明 |
|------|------|
| **角色** | 管理内容的迭代修改，支持多版本对比和回滚 |
| **输入** | M-09/M-10 的初版内容 + 后续修改指令 |
| **输出** | `VersionedContent` — 带版本链的完整内容对象 |

**版本链示例:**
```
cnt_img_20260712_001 (小红书图文)
├── v1.0  2026-07-12T09:10  [初始生成]    标题:"夏天这样穿..."
├── v1.1  2026-07-12T09:30  [AI优化]      标题改为:"夏日穿搭公式！3套直接抄"
│       变更: title, body(润色), 增加 hashtag #穿搭公式
├── v1.2  2026-07-12T09:45  [AI优化]      替换图片 img_look1 → img_look1_v2
│       变更: images[0].url
└── v2.0  2026-07-12T10:00  [人工修改]    调整 body 语气，删除 mention
        变更: body, mention_accounts
        状态: current
```

**版本数据结构:**
```json
{
  "content_id": "cnt_img_20260712_001",
  "current_version": "v2.0",
  "versions": [
    {
      "version": "v1.0",
      "created_at": "2026-07-12T09:10:00Z",
      "created_by": "ai_generator",
      "snapshot": { /* 完整内容快照 */ },
      "parent": null
    },
    {
      "version": "v2.0",
      "created_at": "2026-07-12T10:00:00Z",
      "created_by": "human_editor_001",
      "snapshot": { /* 完整内容快照 */ },
      "parent": "v1.2",
      "diff": {
        "body": "diff --git a/body b/body\n@@ -1,3 +1,3 @@\n-姐妹们！今天分享...\n+大家好！今天分享...",
        "mention_accounts": "removed"
      }
    }
  ],
  "version_graph": "v1.0 → v1.1 → v1.2 → v2.0"
}
```

### M-12 — 内容封装 (Content Package)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环收尾，将所有平台的内容打包为统一格式 |
| **输入** | M-11 的 `VersionedContent[]` (current version) |
| **输出** | `ContentPack` + `content_pack_ready` 事件 |

**输出示例:**
```json
{
  "pack_id": "pck_20260712_001",
  "plan_id": "pln_20260712_001",
  "created_at": "2026-07-12T10:05:00Z",
  "status": "pending_review",
  "contents": [
    {
      "content_id": "cnt_img_20260712_001",
      "platform": "小红书",
      "format": "图文",
      "version": "v2.0",
      "scheduled_time": "2026-07-13T12:00:00+08:00",
      "preview_url": "https://preview.internal/pck_20260712_001/xiaohongshu"
    },
    {
      "content_id": "cnt_vid_20260712_001",
      "platform": "抖音",
      "format": "短视频",
      "version": "v1.0",
      "scheduled_time": "2026-07-13T19:00:00+08:00",
      "preview_url": "https://preview.internal/pck_20260712_001/douyin"
    }
  ],
  "next_trigger": "content_pack_ready → M-13 (审阅入口)"
}
```

---

## 3. 素材到内容的数据转换

```
素材库 ──[M-07 筛选]──▶ SelectedMaterial[] ──[M-08 策划]──▶ ContentPlan
                                                              │
                                    ┌─────────────────────────┤
                                    ▼                         ▼
                              M-09 图文生成              M-10 视频生成
                              ImageTextContent           VideoContent
                                    │                         │
                                    └─────────┬───────────────┘
                                              ▼
                                        M-11 版本管理
                                        VersionedContent
                                              │
                                              ▼
                                        M-12 内容封装
                                        ContentPack
```

| 节点 | 输入 | 输出 | 关键变化 |
|------|------|------|---------|
| M-07 | 素材库 (全部) | SelectedMaterial[] | 按规则筛选，引入 engagement_potential 评分 |
| M-08 | SelectedMaterial[] | ContentPlan | 素材→策划案，增加 platform/tone/angle/schedule |
| M-09 | ContentPlan (图文条目) | ImageTextContent | 策划→具体图文，含排版/配图/hashtag |
| M-10 | ContentPlan (视频条目) | VideoContent | 策划→具体视频，含字幕/BGM/特效 |
| M-11 | ImageTextContent / VideoContent | VersionedContent | 初版→多版本，含 diff 追踪 |
| M-12 | VersionedContent[] | ContentPack | 打包+预览链接+状态标记 |

---

## 4. 平台差异化处理

| 维度 | 小红书 (M-09) | 微博 (M-09) | 抖音 (M-10) | B站 (M-10) |
|------|-------------|------------|------------|-----------|
| **格式** | 图文 (1-9张) | 图文 (1-18张) | 短视频 (15-60s) | 中视频 (1-10min) |
| **标题长度** | ≤20 字 | ≤32 字 | ≤55 字 | ≤80 字 |
| **语气风格** | 亲切分享/种草 | 热点/话题性 | 潮流/娱乐 | 深度/教程 |
| **Hashtag 策略** | 5-10 个精准标签 | 2-3 个热搜话题 | 3-5 个热门标签 | 3-5 个分区标签 |
| **互动元素** | 投票/提问贴纸 | 转发抽奖 | 合拍/评论置顶 | 弹幕互动 |
| **最佳发布时间** | 12:00 / 20:00 | 10:00 / 18:00 | 12:00 / 19:00 / 21:00 | 12:00 / 18:00 |
| **图片尺寸** | 3:4 (1080×1440) | 16:9 / 1:1 | - | - |
| **视频尺寸** | - | - | 9:16 (1080×1920) | 16:9 (1920×1080) |

---

## 5. 版本管理规则 (M-11)

```
版本号规则: 主版本.次版本
  - 次版本升级 (v1.0 → v1.1): AI自动优化, 小范围修改
  - 主版本升级 (v1.x → v2.0): 人工介入修改, 大幅调整

版本状态:
  draft    → 草稿, 未完成
  current  → 当前选中版本
  archived → 归档版本, 不可修改

回滚规则:
  1. 仅支持回滚到同主版本内的任意次版本
  2. 跨主版本回滚需人工确认
  3. 回滚后创建新版本 (如 v1.2 → rollback → v1.3 记录为 "回滚自 v1.0")
```

---

## 6. 调试顺序

```
Step 1: M-07 素材筛选
  ├── 验证: asset_ready 事件能否触发筛选
  ├── 检查: 筛选条件是否生效 (categories, quality_score_min)
  └── 日志关键词: [MaterialSelect] selection_id=xxx, count=N

Step 2: M-08 内容策划
  ├── 验证: 策划案各条目 platform 和 format 是否正确
  ├── 检查: scheduled_time 是否在发布窗口内
  └── 日志关键词: [ContentPlan] plan_id=xxx, entries=N

Step 3: M-09 图文生成
  ├── 验证: 图片生成是否成功, 尺寸是否符合平台要求
  ├── 检查: 正文长度, hashtag 数量
  └── 日志关键词: [ImageTextGen] content_id=xxx, platform=小红书

Step 4: M-10 视频生成
  ├── 验证: 视频文件是否可播放, 字幕时间轴是否正确
  ├── 检查: 分辨率, 时长是否在平台限制内
  └── 日志关键词: [VideoGen] content_id=xxx, duration=N, platform=抖音

Step 5: M-11 版本管理
  ├── 验证: 版本链是否正确 (parent 指向)
  ├── 检查: diff 能否正确回放
  └── 日志关键词: [VersionMgmt] content_id=xxx, current_version=vX.X

Step 6: M-12 内容封装
  ├── 验证: ContentPack 是否包含所有平台内容
  ├── 检查: preview_url 可访问性
  └── 日志关键词: [ContentPack] pack_id=xxx, status=pending_review

E2E:
  ├── 从 asset_ready 到 content_pack_ready 事件
  ├── 验证各平台预览链接可用
  └── 检查 版本管理中的 diff 完整性
```

---

## 7. 验收标准

| 编号 | 验收项 | 标准 | 验证方式 |
|------|--------|------|---------|
| AC-01 | 筛选准确性 | M-07 筛选结果严格符合查询条件 (分类/质量分/排除已用) | 集成测试 |
| AC-02 | 策划完整性 | M-08 每条 entry 包含 title/angle/target_platforms/content_brief | Schema 校验 |
| AC-03 | 图文生成质量 | M-09 输出图片尺寸符合目标平台规范，正文无错别字 | 人工抽查 + 自动化检查 |
| AC-04 | 视频生成质量 | M-10 输出视频分辨率 ≥1080p，字幕准确率 ≥95% | 自动化检测 + 人工抽查 |
| AC-05 | 平台适配 | 同一素材在不同平台的内容差异化 (标题长度、语气、标签策略) | 对比测试 |
| AC-06 | 版本链完整 | M-11 每次修改创建新版本，parent 指向正确 | 单元测试 |
| AC-07 | Diff 可追溯 | M-11 版本间 diff 能正确反映变更内容 | 构造修改场景验证 |
| AC-08 | 打包完整性 | M-12 ContentPack 包含所有 target_platforms 的内容 | 计数对比 |
| AC-09 | 预览可用 | M-12 preview_url 在生成后 5 秒内可访问 | HTTP 200 检查 |
| AC-10 | 闭环触发 | M-12 完成时发布 content_pack_ready 事件 | 事件总线监控 |
| AC-11 | 生成性能 | 单条图文生成 ≤15s，单条视频生成 ≤120s | 性能测试 |
| AC-12 | 并发支持 | 同一 plan 下的多平台内容可并行生成 | 并发测试 |
