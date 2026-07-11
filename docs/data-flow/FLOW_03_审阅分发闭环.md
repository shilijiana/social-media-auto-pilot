# FLOW_03: 审阅分发闭环

> 闭环路径: M-13 → M-14/M-15 → M-16 → M-17 → M-18 → M-19
> 闭环目标: 对待发布内容进行审阅决策，通过后分发到各平台并监控发布状态
> 目标读者: Hermes Agent

---

## 1. ASCII 流程图

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      审阅分发闭环 (Review & Publish Loop)                       │
│                                                                              │
│   ┌──────────┐                                                              │
│   │  M-13    │     content_pack_ready 事件                                   │
│   │ 审阅入口 │                                                              │
│   │ (Entry)  │                                                              │
│   │          │                                                              │
│   │ 决策:    │                                                              │
│   │ A/B/C    │                                                              │
│   └────┬─────┘                                                              │
│        │                                                                    │
│   ┌────┼────────────────────────┐                                           │
│   ▼    ▼                        ▼                                           │
│  ┌──────────┐            ┌──────────────┐                                   │
│  │  M-14    │            │   M-15       │                                   │
│  │ 自动审阅 │            │  人工审阅    │                                   │
│  │ (Auto)   │            │  (Manual)    │                                   │
│  │          │            │              │                                   │
│  │ 模式 A:  │            │  模式 B:     │                                   │
│  │ 全自动   │            │  人工复核    │                                   │
│  │          │            │              │                                   │
│  │ 模式 C:  │            │  审核界面:   │                                   │
│  │ 混合模式 │            │  - 预览      │                                   │
│  │ (A+B)    │            │  - 批注      │                                   │
│  └────┬─────┘            │  - 驳回/通过 │                                   │
│       │                  └──────┬───────┘                                   │
│       │                         │                                           │
│       └─────────┬───────────────┘                                           │
│                 ▼                                                           │
│          ┌──────────────┐                                                   │
│          │    M-16      │                                                   │
│          │  审阅决策    │                                                   │
│          │  (Decide)    │                                                   │
│          │              │                                                   │
│          │  通过 / 驳回 │                                                   │
│          │  / 修改重审  │                                                   │
│          └──────┬───────┘                                                   │
│                 │                                                           │
│           通过  │  驳回/修改                                                 │
│                 │                                                           │
│                 ▼                                                           │
│          ┌──────────────┐         ┌─────────────────┐                       │
│          │    M-17      │         │  返回 M-11      │                       │
│          │  发布调度    │         │  (版本管理)     │                       │
│          │  (Schedule)  │         │  修改后重新提交  │                       │
│          │              │         └─────────────────┘                       │
│          │ 状态机:      │                                                   │
│          │ PENDING→     │                                                   │
│          │ PUBLISHING→  │                                                   │
│          │ PUBLISHED    │                                                   │
│          └──────┬───────┘                                                   │
│                 │                                                           │
│                 ▼                                                           │
│          ┌──────────────┐                                                   │
│          │    M-18      │                                                   │
│          │  发布执行    │                                                   │
│          │  (Publish)   │                                                   │
│          │              │                                                   │
│          │ 调用各平台   │                                                   │
│          │ API 发布内容  │                                                   │
│          │              │                                                   │
│          │ 重试机制:    │                                                   │
│          │ 3次指数退避  │                                                   │
│          └──────┬───────┘                                                   │
│                 │                                                           │
│                 ▼                                                           │
│          ┌──────────────┐                                                   │
│          │    M-19      │                                                   │
│          │  监控+报告   │                                                   │
│          │  (Monitor)   │                                                   │
│          │              │                                                   │
│          │ 发布状态监控 │                                                   │
│          │ 数据回收     │                                                   │
│          │ 生成发布报告 │                                                   │
│          │ → 闭环结束   │                                                   │
│          └──────────────┘                                                   │
│                                                                              │
│   闭环终点: 发布完成报告 (publish_complete) → 数据反馈至 M-07 素材筛选         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 各模块角色说明

### M-13 — 审阅入口 (Review Entry)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环入口，接收待审阅内容包并路由到合适的审阅模式 |
| **触发** | 监听 `content_pack_ready` 事件 |
| **输入** | M-12 的 `ContentPack` |
| **输出** | 审阅任务 + 审阅模式路由 |

**审阅模式决策 (A/B/C):**

```
决策树:
  content_pack_ready
       │
       ▼
  ┌─────────────┐
  │ 检查内容类型 │
  └──────┬──────┘
         │
    ┌────┼────────────────┐
    ▼    ▼                ▼
  图文  视频            混合包
    │    │                │
    ▼    ▼                ▼
 ┌────┐┌────┐        ┌──────────┐
 │模式││模式│        │ 检查风险 │
 │ A  ││ B  │        │ 评分     │
 └────┘└────┘        └────┬─────┘
                          │
                    ┌─────┼─────┐
                    ▼           ▼
                risk<0.3    risk≥0.3
                    │           │
                    ▼           ▼
                 模式 A      模式 C
                (全自动)    (混合: AI初审+人工复核)
```

**路由示例:**
```json
{
  "review_task_id": "rev_20260712_001",
  "pack_id": "pck_20260712_001",
  "review_mode": "C",
  "mode_reason": "risk_score=0.45 (视频内容+首次发布新平台)",
  "auto_review": {
    "assigned": true,
    "reviewer": "ai_reviewer_v2"
  },
  "manual_review": {
    "assigned": true,
    "reviewer_queue": "senior_editors",
    "deadline": "2026-07-13T08:00:00+08:00"
  },
  "created_at": "2026-07-12T10:10:00Z"
}
```

### M-14 — 自动审阅 (Auto Review)

| 属性 | 说明 |
|------|------|
| **角色** | AI 驱动的自动内容审核 |
| **输入** | ContentPack 中的内容 |
| **输出** | `AutoReviewResult` — 包含合规检查、质量评分、优化建议 |

**审阅维度:**
```json
{
  "review_id": "autorev_20260712_001",
  "pack_id": "pck_20260712_001",
  "completed_at": "2026-07-12T10:11:00Z",
  "results": [
    {
      "content_id": "cnt_img_20260712_001",
      "checks": {
        "compliance": {
          "passed": true,
          "checks": [
            {"rule": "no_sensitive_words", "passed": true},
            {"rule": "no_false_advertising", "passed": true},
            {"rule": "copyright_check", "passed": true, "similarity": 0.12},
            {"rule": "platform_policy", "passed": true, "platform": "小红书"}
          ]
        },
        "quality": {
          "score": 0.88,
          "dimensions": {
            "readability": 0.92,
            "engagement_potential": 0.85,
            "visual_appeal": 0.90,
            "seo_score": 0.85
          }
        },
        "suggestions": [
          {
            "type": "improvement",
            "priority": "low",
            "message": "建议在正文第一段增加互动引导语"
          }
        ]
      },
      "verdict": "approved",
      "confidence": 0.95
    }
  ],
  "summary": {
    "total": 2,
    "approved": 2,
    "flagged": 0,
    "rejected": 0
  }
}
```

### M-15 — 人工审阅 (Manual Review)

| 属性 | 说明 |
|------|------|
| **角色** | 人工编辑的审阅工作台 |
| **输入** | ContentPack + M-14 的 AutoReviewResult (模式 C 时) |
| **输出** | `ManualReviewResult` — 通过/驳回/修改意见 |

**审阅工作台数据结构:**
```json
{
  "review_id": "manrev_20260712_001",
  "pack_id": "pck_20260712_001",
  "reviewer_id": "editor_zhang",
  "status": "in_progress",
  "started_at": "2026-07-12T10:30:00Z",
  "auto_review_ref": "autorev_20260712_001",
  "decisions": [
    {
      "content_id": "cnt_img_20260712_001",
      "verdict": "approved",
      "comment": "内容质量不错，自动审阅意见已确认",
      "edited_fields": []
    },
    {
      "content_id": "cnt_vid_20260712_001",
      "verdict": "needs_revision",
      "comment": "视频前3秒不够吸引人，BGM音量偏高",
      "required_changes": [
        {"field": "content.video_url", "instruction": "重新剪辑前3秒，增加钩子画面"},
        {"field": "content.bgm.volume", "instruction": "将BGM音量从 0.3 调至 0.2"}
      ]
    }
  ]
}
```

### M-16 — 审阅决策 (Review Decide)

| 属性 | 说明 |
|------|------|
| **角色** | 汇总审阅结果并做出最终决策 |
| **输入** | M-14 和/或 M-15 的审阅结果 |
| **输出** | 最终决策: approved / rejected / needs_revision |

**决策逻辑:**
```
┌──────────────────────────────────────────────────────┐
│                    审阅决策流程                        │
│                                                      │
│  模式 A (纯自动):                                     │
│    M-14 verdict == approved → 直接通过                │
│    M-14 verdict == flagged  → 升级为模式 B             │
│    M-14 verdict == rejected → 驳回                    │
│                                                      │
│  模式 B (纯人工):                                     │
│    M-15 verdict == approved → 通过                    │
│    M-15 verdict == rejected → 驳回                    │
│    M-15 verdict == needs_revision → 修改重审           │
│                                                      │
│  模式 C (混合):                                       │
│    M-14 approved AND M-15 approved → 通过              │
│    M-14 rejected OR  M-15 rejected  → 驳回            │
│    任一 needs_revision → 修改重审                      │
│    M-14 与 M-15 冲突 → 升级人工裁决                    │
└──────────────────────────────────────────────────────┘
```

**决策输出示例:**
```json
{
  "decision_id": "dec_20260712_001",
  "pack_id": "pck_20260712_001",
  "decided_at": "2026-07-12T10:35:00Z",
  "per_content": [
    {
      "content_id": "cnt_img_20260712_001",
      "final_verdict": "approved",
      "publish_ready": true
    },
    {
      "content_id": "cnt_vid_20260712_001",
      "final_verdict": "needs_revision",
      "publish_ready": false,
      "next_action": "return_to_M11",
      "revision_deadline": "2026-07-12T14:00:00+08:00"
    }
  ],
  "summary": {
    "approved_count": 1,
    "rejected_count": 0,
    "revision_count": 1
  }
}
```

### M-17 — 发布调度 (Publish Schedule)

| 属性 | 说明 |
|------|------|
| **角色** | 管理发布状态机，按计划时间调度发布任务 |
| **输入** | M-16 的 approved 内容 + 预定发布时间 |
| **输出** | `PublishTask[]` — 带时间窗口的发布任务队列 |

**发布状态机:**
```
                    ┌─────────┐
                    │ PENDING │  ← 初始状态 (已通过审阅, 等待发布时间)
                    └────┬────┘
                         │ 到达 scheduled_time
                         ▼
                    ┌──────────┐
          ┌────────│SCHEDULED │
          │        └────┬─────┘
          │             │ 调度器拾取
          │             ▼
          │        ┌───────────┐
          │   ┌───▶│PUBLISHING │  ← 正在调用平台 API
          │   │    └─────┬─────┘
          │   │          │
          │   │     ┌────┼────────┐
          │   │     ▼    ▼        ▼
          │   │  ┌──────┐ ┌──────┐ ┌─────────┐
          │   │  │ 成功  │ │ 失败 │ │ 部分成功 │
          │   │  └──┬───┘ └──┬───┘ └────┬────┘
          │   │     │        │          │
          │   │     ▼        ▼          ▼
          │   │  ┌───────┐┌───────┐┌──────────┐
          │   │  │PUBLISH││RETRY  ││PARTIAL   │
          │   │  │ED     ││       ││PUBLISHED │
          │   │  └───────┘└───┬───┘└────┬─────┘
          │   │               │         │
          │   │         重试次数<3?     │
          │   │          │    │         │
          │   │         是   否         │
          │   │          │    │         │
          │   └──────────┘    ▼         │
          │              ┌────────┐     │
          │              │FAILED  │     │
          │              └────────┘     │
          │                             │
          └─────────────────────────────┘
                   (重试: PUBLISHING)
```

**发布任务示例:**
```json
{
  "task_id": "pub_20260713_001",
  "content_id": "cnt_img_20260712_001",
  "platform": "小红书",
  "status": "PENDING",
  "scheduled_time": "2026-07-13T12:00:00+08:00",
  "publish_window": {
    "start": "2026-07-13T11:55:00+08:00",
    "end": "2026-07-13T12:15:00+08:00"
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff_strategy": "exponential",
    "base_delay_seconds": 30,
    "max_delay_seconds": 300
  },
  "created_at": "2026-07-12T10:35:00Z"
}
```

### M-18 — 发布执行 (Publish Execute)

| 属性 | 说明 |
|------|------|
| **角色** | 调用各社交媒体平台 API 执行实际发布 |
| **输入** | M-17 的 `PublishTask` |
| **输出** | `PublishResult` — 发布状态 + 平台返回的 post_id/url |

**发布执行流程:**
```
PublishTask
    │
    ▼
┌───────────────┐
│ 平台适配器选择 │ ← 根据 platform 字段路由
└───────┬───────┘
        │
   ┌────┼────────────┬────────────┐
   ▼    ▼            ▼            ▼
┌──────┐┌──────┐┌──────┐┌──────────┐
│小红书 ││ 微博  ││ 抖音  ││  B站     │
│Adapter││Adapter││Adapter││ Adapter  │
└──┬───┘└──┬───┘└──┬───┘└────┬─────┘
   │       │       │         │
   ▼       ▼       ▼         ▼
┌──────────────────────────────────┐
│         平台 API 调用             │
│  POST /api/v2/post/create        │
│  Headers: Authorization, ...     │
│  Body: { title, content, media } │
└──────────────────────────────────┘
```

**发布结果示例 (成功):**
```json
{
  "publish_result_id": "pubres_20260713_001",
  "task_id": "pub_20260713_001",
  "platform": "小红书",
  "status": "PUBLISHED",
  "platform_post_id": "xiaohongshu_post_abc123",
  "platform_post_url": "https://www.xiaohongshu.com/explore/abc123",
  "published_at": "2026-07-13T12:00:05+08:00",
  "api_response_time_ms": 1200,
  "attempt": 1
}
```

**发布结果示例 (失败 → 重试):**
```json
{
  "publish_result_id": "pubres_20260713_002",
  "task_id": "pub_20260713_002",
  "platform": "抖音",
  "status": "RETRYING",
  "attempt": 2,
  "error": {
    "code": "RATE_LIMITED",
    "message": "API rate limit exceeded",
    "retry_after_seconds": 60
  },
  "next_retry_at": "2026-07-13T12:01:30+08:00"
}
```

### M-19 — 监控+报告 (Monitor & Report)

| 属性 | 说明 |
|------|------|
| **角色** | 闭环收尾，监控发布后状态并生成完整报告 |
| **输入** | M-18 的 `PublishResult[]` + 发布后数据回收 |
| **输出** | `PublishReport` + 数据反馈 |

**监控维度:**

| 维度 | 检查项 | 频率 | 告警阈值 |
|------|--------|------|---------|
| 发布状态 | 是否成功发布到平台 | 实时 | 发布失败立即告警 |
| 内容可见性 | 内容是否被平台屏蔽/限流 | 发布后 5min/30min/2h | 不可见立即告警 |
| 互动数据 | 点赞/评论/转发/播放量 | 发布后 1h/6h/24h/72h | 低于同类型均值 50% |
| 负面反馈 | 举报/负面评论/踩 | 实时监控 | 举报数 > 3 条 |

**发布报告示例:**
```json
{
  "report_id": "rpt_pub_20260713_001",
  "pack_id": "pck_20260712_001",
  "generated_at": "2026-07-13T12:10:00Z",
  "publish_summary": {
    "total_tasks": 2,
    "published": 1,
    "failed": 0,
    "partial": 1,
    "pending": 0
  },
  "per_platform": [
    {
      "content_id": "cnt_img_20260712_001",
      "platform": "小红书",
      "status": "PUBLISHED",
      "post_url": "https://www.xiaohongshu.com/explore/abc123",
      "published_at": "2026-07-13T12:00:05+08:00",
      "initial_metrics": {
        "views": 0,
        "likes": 0,
        "comments": 0,
        "collected_at": "2026-07-13T12:05:00Z"
      }
    },
    {
      "content_id": "cnt_vid_20260712_001",
      "platform": "抖音",
      "status": "PARTIAL_PUBLISHED",
      "note": "视频发布成功，但话题标签关联失败",
      "post_url": "https://www.douyin.com/video/def456",
      "errors": ["hashtag_link_failed: #OOTD"]
    }
  ],
  "data_feedback": {
    "high_performing_categories": ["时尚穿搭"],
    "engagement_signals": "待后续回收",
    "next_trigger": "反馈数据 → M-07 素材筛选 (优化筛选权重)"
  },
  "closed_loop": true
}
```

---

## 3. 审阅模式决策流

```
                     content_pack_ready
                           │
                           ▼
                  ┌─────────────────┐
                  │  风险评估引擎    │
                  │  (Risk Engine)  │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     risk < 0.3      0.3 ≤ risk     risk ≥ 0.7
     且非首次发布      < 0.7         或敏感内容
            │              │              │
            ▼              ▼              ▼
        ┌──────┐      ┌──────┐      ┌──────────┐
        │模式 A│      │模式 C│      │ 模式 B   │
        │全自动│      │混合  │      │ 纯人工   │
        └──┬───┘      └──┬───┘      └────┬─────┘
           │             │               │
           ▼             ▼               ▼
        M-14 自动     M-14 自动       M-15 人工
        审阅          审阅 +          审阅
                      M-15 人工
                      复核
```

**风险评估因子:**
```json
{
  "risk_factors": {
    "content_type_risk": {
      "图文": 0.1,
      "视频": 0.3,
      "直播预告": 0.5
    },
    "platform_risk": {
      "first_time_publish": 0.2,
      "new_account": 0.3,
      "established_account": 0.0
    },
    "category_risk": {
      "时尚穿搭": 0.1,
      "金融理财": 0.6,
      "医疗健康": 0.7
    },
    "sensitive_keyword_count": "每命中1个关键词 +0.15"
  }
}
```

---

## 4. 重试逻辑详解 (M-18)

```
发布失败
    │
    ▼
┌─────────────┐
│ 错误分类    │
└──────┬──────┘
       │
  ┌────┼────────────────┐
  ▼    ▼                ▼
可重试              不可重试
错误                错误
  │                    │
  ▼                    ▼
重试计数 < 3?      ┌──────────┐
  │                │ 标记     │
  ├── 是           │ FAILED   │
  │   │            │ 人工介入 │
  │   ▼            └──────────┘
  │  计算退避时间
  │  delay = base × 2^(attempt-1)
  │  delay = min(delay, max_delay)
  │   │
  │   ▼
  │  sleep(delay)
  │   │
  │   ▼
  │  重新执行 M-18
  │
  └── 否
      │
      ▼
   ┌──────────┐
   │ 标记     │
   │ FAILED   │
   │ 人工介入 │
   └──────────┘
```

**可重试错误码:**
| 错误码 | 含义 | 退避策略 |
|--------|------|---------|
| `RATE_LIMITED` | API 频率限制 | 使用 API 返回的 retry_after |
| `NETWORK_ERROR` | 网络超时/中断 | 指数退避 30s/60s/120s |
| `SERVER_ERROR_5XX` | 平台服务器错误 | 指数退避 60s/120s/240s |
| `AUTH_EXPIRED` | Token 过期 | 刷新 Token 后立即重试 |

**不可重试错误码:**
| 错误码 | 含义 | 处理 |
|--------|------|------|
| `CONTENT_REJECTED` | 内容被平台拒绝 | 标记 FAILED，通知人工审核 |
| `ACCOUNT_SUSPENDED` | 账号被封禁 | 标记 FAILED，紧急告警 |
| `INVALID_CONTENT` | 内容格式不合法 | 标记 FAILED，检查 M-09/M-10 |
| `AUTH_REVOKED` | 授权被撤销 | 标记 FAILED，要求重新授权 |

---

## 5. 调试顺序

```
Step 1: M-13 审阅入口
  ├── 验证: content_pack_ready 事件能否到达 M-13
  ├── 检查: 审阅模式路由是否正确 (A/B/C 分支)
  └── 日志关键词: [ReviewEntry] pack_id=xxx, mode=X, risk_score=Y

Step 2: M-14 自动审阅
  ├── 验证: 合规检查规则是否全部执行
  ├── 检查: quality_score 各维度分数是否在 0-1 范围
  └── 日志关键词: [AutoReview] review_id=xxx, approved=N, flagged=N

Step 3: M-15 人工审阅
  ├── 验证: 审阅工作台能否正确加载内容预览
  ├── 检查: 批注和修改意见是否正确回传
  └── 日志关键词: [ManualReview] reviewer_id=xxx, verdict=approved/rejected

Step 4: M-16 审阅决策
  ├── 验证: 三种模式的决策逻辑是否按预期执行
  ├── 检查: needs_revision 是否正确触发 M-11
  └── 日志关键词: [ReviewDecide] decision_id=xxx, approved=N, revision=N

Step 5: M-17 发布调度
  ├── 验证: 状态机转换是否正确
  ├── 检查: scheduled_time 触发是否准时 (±1min)
  └── 日志关键词: [PublishSchedule] task_id=xxx, status=PENDING→SCHEDULED→PUBLISHING

Step 6: M-18 发布执行
  ├── 验证: 平台 API 调用是否成功
  ├── 检查: 重试逻辑 (模拟 RATE_LIMITED/NETWORK_ERROR)
  └── 日志关键词: [PublishExec] task_id=xxx, platform=xxx, status=PUBLISHED/FAILED

Step 7: M-19 监控+报告
  ├── 验证: 发布后内容可见性检查
  ├── 检查: 报告字段完整性
  └── 日志关键词: [PublishReport] report_id=xxx, published=N, failed=N

E2E:
  ├── 从 content_pack_ready 到 publish_complete 全链路
  ├── 模拟审阅驳回 → 修改 → 重新审阅 → 发布
  └── 模拟发布失败 → 重试成功
```

---

## 6. 验收标准

| 编号 | 验收项 | 标准 | 验证方式 |
|------|--------|------|---------|
| AC-01 | 审阅路由 | M-13 根据 risk_score 正确选择 A/B/C 模式，准确率 100% | 测试用例覆盖所有分支 |
| AC-02 | 自动审阅完整 | M-14 覆盖合规检查、质量评分、优化建议三类检查 | 检查项计数 |
| AC-03 | 人工审阅可用 | M-15 支持预览、批注、通过、驳回、修改重审 5 种操作 | 功能测试 |
| AC-04 | 决策一致性 | M-16 模式 C 下 M-14 和 M-15 冲突时升级人工裁决 | 冲突场景测试 |
| AC-05 | 状态机正确 | M-17 状态转换路径符合定义，不存在非法跳转 | 状态机测试 |
| AC-06 | 定时准确性 | M-17 在 scheduled_time ±1min 内触发发布 | 时间精度测试 |
| AC-07 | 发布成功率 | M-18 正常网络条件下发布成功率 ≥ 99% | 集成测试 |
| AC-08 | 重试有效性 | M-18 可重试错误在 3 次内恢复成功率 ≥ 80% | 故障注入测试 |
| AC-09 | 不可重试处理 | 不可重试错误正确标记 FAILED 并发送通知 | 错误处理测试 |
| AC-10 | 监控覆盖 | M-19 覆盖发布状态、内容可见性、互动数据、负面反馈 4 个维度 | 监控项检查 |
| AC-11 | 报告完整性 | M-19 报告包含 publish_summary + per_platform + data_feedback | JSON Schema 校验 |
| AC-12 | 闭环反馈 | M-19 产出数据反馈，可被 M-07 消费以优化筛选策略 | 端到端数据流验证 |
| AC-13 | 端到端延迟 | 从 content_pack_ready 到 publish_complete ≤ 5 分钟 (不含人工等待) | 性能测试 |
