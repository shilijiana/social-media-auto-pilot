# default_rules.yaml 审阅规则参考

> 本文档详细说明 `config/review_rules/default_rules.yaml` 中四条默认审阅规则（R001-R004）的含义和使用场景。
> 目标受众: Hermes Agent, 开发人员, 审阅运营人员

---

## 配置文件位置

```
config/review_rules/default_rules.yaml
```

---

## 完整配置结构

```yaml
rules:
  - id: R001
    name: "图片清晰度检查"
    category: "素材"
    expression: "image.resolution_width >= 1920"
    priority: 1
    enabled: true
  - id: R002
    name: "视频时长检查"
    category: "素材"
    expression: "video.duration_sec <= platform.max_duration"
    priority: 1
    enabled: true
  - id: R003
    name: "文案敏感词检查"
    category: "内容"
    expression: "not contains_any(text, sensitive_words)"
    priority: 1
    enabled: true
  - id: R004
    name: "封面尺寸检查"
    category: "内容"
    expression: "image.aspect_ratio == platform.recommended_ratio"
    priority: 2
    enabled: true
```

---

## 规则字段说明

每条规则包含以下通用字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 规则唯一标识，格式 R + 3位数字 |
| `name` | string | 是 | 规则名称（中文） |
| `category` | string | 是 | 规则分类：素材 / 内容 |
| `expression` | string | 是 | 规则表达式，用于自动判定是否通过 |
| `priority` | integer | 是 | 优先级：1=必须通过, 2=建议通过, 3=仅供参考 |
| `enabled` | boolean | 是 | 是否启用该规则 |

### 优先级说明

| 优先级 | 名称 | 说明 | 不通过时 |
|--------|------|------|---------|
| 1 | 必须通过 | 阻塞性规则，必须通过才能继续 | 整体 `overall_passed = false` |
| 2 | 建议通过 | 非阻塞性规则，不通过会标记警告 | 标记但继续流程 |
| 3 | 仅供参考 | 信息性规则，仅用于数据收集 | 不影响流程 |

---

## R001 — 图片清晰度检查

### 基本信息

| 属性 | 值 |
|------|-----|
| **规则 ID** | R001 |
| **规则名称** | 图片清晰度检查 |
| **分类** | 素材 |
| **优先级** | 1（必须通过） |
| **状态** | 已启用 |

### 表达式

```
image.resolution_width >= 1920
```

### 规则详解

| 检查项 | 说明 |
|--------|------|
| **检查对象** | 所有图片类素材（type=image） |
| **检查标准** | 图片宽度 >= 1920 像素 |
| **检查逻辑** | 读取素材的 `resolution.width` 字段，与阈值 1920 比较 |
| **通过条件** | `resolution.width >= 1920` |
| **不通过时** | 标记为 `passed=false`，建议替换高清素材 |
| **不通过的后果** | 阻塞内容生产流程（priority=1） |

### 适用场景

- 素材采集阶段（M-02）：采集时过滤低清晰度图片
- 素材去重阶段（M-05）：质量评分参考
- 封面图生成（M-09）：确保封面素材清晰度足够

### 修改建议

当检查不通过时，系统会生成以下建议：

```
"detail": "素材清晰度不达标：宽度 1280px < 1920px 最低要求"
"suggestion": "请替换为分辨率不低于 1920×1080 的高清素材"
```

### 扩展配置

可根据实际需求扩展为更详细的清晰度规则：

```yaml
- id: R001
  name: "图片清晰度检查"
  category: "素材"
  expression: "image.resolution_width >= 1920 AND image.clarity_score >= 70"
  priority: 1
  enabled: true
```

---

## R002 — 视频时长检查

### 基本信息

| 属性 | 值 |
|------|-----|
| **规则 ID** | R002 |
| **规则名称** | 视频时长检查 |
| **分类** | 素材 |
| **优先级** | 1（必须通过） |
| **状态** | 已启用 |

### 表达式

```
video.duration_sec <= platform.max_duration
```

### 规则详解

| 检查项 | 说明 |
|--------|------|
| **检查对象** | 所有视频类素材（type=video） |
| **检查标准** | 视频时长 <= 目标平台最大时长限制 |
| **检查逻辑** | 读取素材的 `duration` 字段，与 `compliance_rules.yaml` 中对应平台的 `max_video_duration_sec` 比较 |
| **通过条件** | `duration <= platform.max_video_duration_sec` |
| **不通过时** | 标记为 `passed=false`，建议剪辑或分割视频 |
| **不通过的后果** | 阻塞内容生产流程（priority=1） |

### 各平台时长限制

| 平台 | 最大时长 | 来源配置 |
|------|---------|---------|
| 抖音 | 900 秒（15 分钟） | `compliance_rules.yaml → platform_rules.douyin.max_video_duration_sec` |
| 小红书 | 无明确限制（以图片为主） | - |
| B站 | 3600 秒（60 分钟） | `compliance_rules.yaml → platform_rules.bilibili.max_video_duration_sec` |
| X(Twitter) | 140 秒（普通用户） | `compliance_rules.yaml → platform_rules.twitter` |

### 适用场景

- 视频素材采集（M-03）：采集时检查时长
- 视频初剪（M-10）：剪辑后检查是否符合平台要求
- 多平台分发（M-16）：分发前按目标平台验证

### 修改建议

当检查不通过时，系统会生成以下建议：

```
"detail": "视频时长 1200 秒超出抖音限制 900 秒"
"suggestion": "建议将视频剪辑至 15 分钟以内，或将超长内容分割为系列视频"
```

---

## R003 — 文案敏感词检查

### 基本信息

| 属性 | 值 |
|------|-----|
| **规则 ID** | R003 |
| **规则名称** | 文案敏感词检查 |
| **分类** | 内容 |
| **优先级** | 1（必须通过） |
| **状态** | 已启用 |

### 表达式

```
not contains_any(text, sensitive_words)
```

### 规则详解

| 检查项 | 说明 |
|--------|------|
| **检查对象** | 所有内容的文案（`copytext` 和 `title` 字段） |
| **检查标准** | 文案中不包含 `compliance_rules.yaml` 中 `sensitive_words` 列表中的任何词 |
| **检查逻辑** | 遍历敏感词列表，检查文案中是否包含（子串匹配） |
| **通过条件** | 文案不包含任何敏感词 |
| **不通过时** | 标记为 `passed=false`，列出匹配到的敏感词和位置 |
| **不通过的后果** | 阻塞内容发布流程（priority=1） |

### 敏感词列表

当前配置的敏感词来自 `compliance_rules.yaml`：

```
第一, 最好, 最, 国家级, 世界级, 唯一, 顶级, 绝对
```

### 适用场景

- 文案生成后检查（M-08 → M-12）
- 内容精加工阶段（M-11）
- 发布前最终检查（M-16 分发前）

### 修改建议

当检查不通过时，系统会生成以下建议：

```
"detail": "文案中包含敏感词'最'（位置：第3段），可能违反广告法"
"suggestion": "将'最先进的技术'修改为'前沿技术'或'领先的技术'"
```

### 扩展配置

可根据需要细化敏感词检查规则：

```yaml
- id: R003
  name: "文案敏感词检查"
  category: "内容"
  expression: "not contains_any(text, sensitive_words) AND not contains_any(text, competitor_names)"
  priority: 1
  enabled: true
```

---

## R004 — 封面尺寸检查

### 基本信息

| 属性 | 值 |
|------|-----|
| **规则 ID** | R004 |
| **规则名称** | 封面尺寸检查 |
| **分类** | 内容 |
| **优先级** | 2（建议通过） |
| **状态** | 已启用 |

### 表达式

```
image.aspect_ratio == platform.recommended_ratio
```

### 规则详解

| 检查项 | 说明 |
|--------|------|
| **检查对象** | 所有内容的封面图 |
| **检查标准** | 封面图宽高比 == 目标平台推荐宽高比 |
| **检查逻辑** | 读取封面图的 `resolution.width/height`，计算宽高比，与 `compliance_rules.yaml` 中对应平台的 `recommended_ratio` 比较 |
| **通过条件** | 宽高比与推荐值偏差在 ±5% 以内 |
| **不通过时** | 标记为 `passed=false`，建议调整封面尺寸 |
| **不通过的后果** | 仅标记警告，不阻塞流程（priority=2） |

### 各平台推荐宽高比

| 平台 | 推荐比例 | 最佳尺寸 | 来源配置 |
|------|---------|---------|---------|
| 抖音 | 9:16 | 1080×1920 | `platform_rules.douyin.recommended_ratio` |
| 小红书 | 3:4 | 1080×1440 | `platform_rules.xiaohongshu.recommended_ratio` |
| B站 | 16:9 | 1920×1080 | `platform_rules.bilibili.recommended_ratio` |
| X(Twitter) | 1:1 | 1200×1200 | `platform_rules.twitter.recommended_ratio` |

### 适用场景

- 封面图生成（M-09）：生成封面时按平台推荐比例输出
- 内容精加工（M-11）：定稿前检查封面是否符合平台规范
- 多平台分发（M-16）：分发到不同平台时自动裁剪/调整

### 修改建议

当检查不通过时，系统会生成以下建议：

```
"detail": "封面图宽高比 4:3 不符合抖音推荐的 9:16"
"suggestion": "建议将封面图调整为 9:16 竖版尺寸（推荐 1080×1920），或使用 M-09 重新生成"
```

### 注意

- 此规则优先级为 2（建议通过），不通过时不阻塞发布
- 但建议在 M-09 封面图生成阶段就按平台推荐比例生成，避免后续调整

---

## 规则执行流程

```
M-11 内容精加工与定稿
      │
      ▼
M-12 合规性自检
      │
      ├── R001: 图片清晰度检查 ──────► 素材域检查
      │   └── resolution.width >= 1920
      │
      ├── R002: 视频时长检查 ────────► 素材域检查
      │   └── duration <= platform.max_duration
      │
      ├── R003: 文案敏感词检查 ──────► 内容域检查
      │   └── not contains_any(text, sensitive_words)
      │
      └── R004: 封面尺寸检查 ────────► 内容域检查
          └── aspect_ratio == platform.recommended_ratio
      │
      ▼
ComplianceResult
  ├── check_items: [R001结果, R002结果, R003结果, R004结果]
  ├── overall_passed: 所有 priority=1 的规则均通过
  └── 返回 M-11
```

---

## 添加新规则

### 规则模板

```yaml
- id: R005                          # 新规则 ID（递增）
  name: "规则名称"                    # 中文描述
  category: "素材"                   # 素材 / 内容
  expression: "条件表达式"            # 判定逻辑
  priority: 1                        # 1/2/3
  enabled: true                      # true/false
```

### 示例：添加"视频码率检查"规则

```yaml
- id: R005
  name: "视频码率检查"
  category: "素材"
  expression: "video.bitrate >= 1000000"
  priority: 2
  enabled: true
```

### 示例：添加"文案长度检查"规则

```yaml
- id: R006
  name: "文案长度检查"
  category: "内容"
  expression: "text.length <= platform.max_text_length"
  priority: 1
  enabled: true
```

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **对应文件**: `config/review_rules/default_rules.yaml`
