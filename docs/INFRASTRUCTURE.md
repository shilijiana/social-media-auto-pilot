# Hermes 智能体 — 共享基础设施文档

> 本文档覆盖 Hermes 智能体所有共享基础设施模块的配置、常用操作与调试清单。
> ��有内容使用中文编写，面向开发与运维人员。

---

## 目录

1. [数据库](#1-数据库)
2. [文件存储](#2-文件存储)
3. [LLM 调用](#3-llm-调用)
4. [浏览器自动化](#4-浏览器自动化)
5. [媒体处理](#5-媒体处理)
6. [API 路由](#6-api-路由)
7. [任务调度](#7-任务调度)
8. [配置文件参考](#8-配置文件参考)

---

## 1. 数据库

### 1.1 配置参考

**主配置文件**: `config/settings.yaml` → `database` 节点

```yaml
database:
  url: sqlite:///data/db/social_auto_pilot.db   # 默认 SQLite
  # url: postgresql://user:pass@host:5432/hermes # 生产环境 PostgreSQL
  echo: false                                     # 是否输出 SQL 日志
  pool_size: 5                                    # 连接池大小
  pool_recycle: 3600                              # 连接回收时间 (秒)
```

**环境变量覆盖**:

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `DATABASE_URL` | 完整数据库连接串 | `sqlite:///data/db/social_auto_pilot.db` |
| `DB_ECHO` | 开启 SQL 日志 | `true` / `false` |

默认使用 **SQLite**，数据库文件位于 `data/db/social_auto_pilot.db`。生产环境建议切换为 PostgreSQL。

### 1.2 ORM 模型

所有 ORM 模型定义在 `src/models/` 目录下，共 6 个模块：

| 文件 | 对应模块 | 核心模型 |
|------|---------|---------|
| `src/models/material.py` | 素材库 (M-01~M-06) | `Material`, `MaterialTag`, `MaterialVersion` |
| `src/models/content.py` | 内容工厂 (M-07~M-12) | `Content`, `ContentScript`, `ContentAsset` |
| `src/models/review.py` | 审核系统 (M-13~M-17) | `ReviewTask`, `ReviewResult`, `ReviewRule` |
| `src/models/distribute.py` | 分发引擎 (M-18~M-24) | `DistributeTask`, `PlatformAccount`, `PublishRecord` |
| `src/models/analytics.py` | 数据分析 (M-25~M-27) | `AnalyticsReport`, `MetricSnapshot`, `Dashboard` |
| `src/models/learning.py` | 学习进化 (M-28~M-30) | `LearningSession`, `StrategyUpdate`, `ABTest` |

### 1.3 常用操作

```bash
# 初始化数据库（创建所有表）
python scripts/init_db.py

# 仅创建指定模块的表
python scripts/init_db.py --module content

# 查看当前数据库 schema
python scripts/show_schema.py

# 查看 schema 并输出到文件
python scripts/show_schema.py --output schema_dump.txt

# 重置数据库（危险操作，需确认）
python scripts/init_db.py --reset --confirm

# 迁移数据库（Alembic）
alembic upgrade head
alembic downgrade -1
alembic history

# 生成迁移脚本
alembic revision --autogenerate -m "描述本次变更"

# 查看数据库统计信息
python scripts/db_stats.py

# 备份 SQLite 数据库
cp data/db/social_auto_pilot.db data/db/backup_$(date +%Y%m%d_%H%M%S).db
```

### 1.4 调试清单

- [ ] 数据库文件是否存在: `ls -la data/db/social_auto_pilot.db`
- [ ] 所有表是否已创建: `python scripts/show_schema.py` 确认 6 个模块的表都已列出
- [ ] ORM 模型与数据库 schema 是否一致: 执行 `alembic check` 或对比模型定义
- [ ] 连接是否正常: `python -c "from src.infrastructure.database import engine; engine.connect()"`
- [ ] 连接池状态: 检查日志中无连接泄漏或超时警告
- [ ] SQLite WAL 模式是否开启: `PRAGMA journal_mode;` 应返回 `wal`

---

## 2. 文件存储

### 2.1 配置参考

**主配置文件**: `config/settings.yaml` → `storage` 节点

```yaml
storage:
  base_path: data/files          # 文件存储根目录
  temp_path: data/files/temp     # 临时文件目录
  max_upload: 524288000          # 最大上传大小 500MB (字节)
  allowed_extensions:            # 允许的文件扩展名
    images: [jpg, jpeg, png, gif, webp, bmp]
    videos: [mp4, mov, avi, mkv, webm]
    audio: [mp3, wav, aac, flac, ogg]
    documents: [pdf, docx, xlsx, pptx, txt, json, csv]
  cleanup_policy:
    temp_ttl: 86400              # 临时文件保留 24 小时
    auto_cleanup: true           # 自动清理过期临时文件
```

### 2.2 目录结构

```
data/files/
├── materials/          # 原始素材
│   ├── images/         #   图片素材 (M-01)
│   ├── videos/         #   视频素材 (M-02)
│   └── audio/          #   音频素��� (M-03)
├── outputs/            # 产出物
│   ├── images/         #   生成/编辑后的图片 (M-07)
│   ├── videos/         #   生成/编辑后的视频 (M-09)
│   └── copywriting/    #   文案产出 (M-08)
├── reports/            # 分析报告
│   ├── daily/          #   日报 (M-25)
│   ├── weekly/         #   周报 (M-26)
│   └── monthly/        #   月报 (M-27)
├── exports/            # 数据导出
└── temp/               # 临时文件 (24h 自动清理)
```

### 2.3 文件命名规范

**格式**: `[选题编号]_[模块名]_[平台]_[版本号]_[日期].[扩展名]`

| 字段 | 说明 | 示例 |
|------|------|------|
| 选题编号 | 选题唯一标识 | `T2026-001` |
| 模块名 | 模块编号 | `M08` (内容工厂-文案生成) |
| 平台 | 目标平台 | `douyin`, `xiaohongshu` |
| 版本号 | 内容版本 | `v1`, `v2`, `final` |
| 日期 | ISO 日期 | `20260712` |

**示例**:
```
T2026-001_M08_douyin_v2_20260712.json      # 抖音文案 v2
T2026-003_M07_xiaohongshu_v1_20260712.png   # 小红书配图 v1
T2026-005_M09_bilibili_final_20260712.mp4   # B站视频终版
```

### 2.4 常用操作

```bash
# 查看各目录占用空间
du -sh data/files/materials/* data/files/outputs/* data/files/reports/*

# 清理过期临时文件
python scripts/cleanup_temp.py

# 手动清理临时目录
rm -rf data/files/temp/*

# 查看磁盘剩余空间
df -h data/files/

# 计算指定选题的所有文件大小
find data/files/ -name "T2026-001_*" -exec du -ch {} + | tail -1

# 归档超过 30 天的报告
find data/files/reports/ -type f -mtime +30 -exec tar -rvf archive.tar {} \; -exec rm {} \;

# 列出最近 7 天修改的文件
find data/files/ -type f -mtime -7 | sort
```

### 2.5 调试清单

- [ ] 所有目录是否已创建:
  ```bash
  for dir in materials/images materials/videos materials/audio \
             outputs/images outputs/videos outputs/copywriting \
             reports/daily reports/weekly reports/monthly \
             exports temp; do
    [ -d "data/files/$dir" ] && echo "OK: $dir" || echo "MISSING: $dir"
  done
  ```
- [ ] 目录是否可写: `touch data/files/temp/write_test && rm data/files/temp/write_test`
- [ ] 磁盘剩余空间 > 1GB: `df -h data/files/ | awk 'NR>1 {print $4}'`
- [ ] 上传大小限制是否生效: 尝试上传 > 500MB 文件应被拒绝
- [ ] 临时文件自动清理是否运行: 检查 `data/files/temp/` 中无超过 24h 的文件
- [ ] 文件权限是否正确: `ls -la data/files/` 确认 owner/group 与运行进程一致

---

## 3. LLM 调用

### 3.1 配置参考

**主配置文件**: `config/settings.yaml` → `llm` 节点

```yaml
llm:
  api_key: ${LLM_API_KEY}        # 从环境变量读取
  base_url: ${LLM_BASE_URL}      # API 基础地址
  model: gpt-4o                   # 主模型 (复杂任务)
  small_model: gpt-4o-mini        # 轻量模型 (简单任务)
  timeout: 60                     # 请求超时 (秒)
  max_retries: 3                  # 最大重试次数
  retry_backoff: 2                # 重试退避倍数
  temperature: 0.7                # 默认温度
  max_tokens: 4096               # 默认最大输出 token
```

**环境变量**:

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `LLM_API_KEY` | API 密钥 | 无 (必填) |
| `LLM_BASE_URL` | API 端点地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 主模型名称 | `gpt-4o` |
| `LLM_SMALL_MODEL` | 轻量模型名称 | `gpt-4o-mini` |

### 3.2 Prompt 模板

所有 Prompt 模板集中管理在 `src/infrastructure/llm/prompts/` 目录：

```
src/infrastructure/llm/prompts/
├── content/               # 内容生成相关
│   ├── copywriting.j2     #   文案生成模板
│   ├── script.j2          #   脚本创作模板
│   └── headline.j2        #   标题优化模板
├── review/                # 审核相关
│   ├── compliance.j2      #   合规审核模板
│   ├── quality.j2         #   质量审核模板
│   └── brand.j2           #   品牌一致性审核
├── analytics/             # 分析相关
│   ├── summary.j2         #   数据摘要模板
│   └── insight.j2         #   洞察生成模板
├── learning/              # 学习相关
│   ├── reflection.j2      #   反思总结模板
│   └── strategy.j2        #   策略建议模板
└── system/                # 系统 Prompt
    ├── base.j2            #   基础系��� Prompt
    └── role_play.j2       #   角色扮演 Prompt
```

模板引擎使用 **Jinja2**，支持变量注入和条件渲染。

### 3.3 调用规范

所有 LLM 调用必须遵循以下规范：

1. **统一接口**: 所有模块通过 `src/infrastructure/llm/client.py` 中的 `LLMClient` 统一调用
2. **可解析 JSON**: 结构化输出必须为合法 JSON，使用 `response_format: json_object`
3. **超时控制**: 默认 60 秒超时，复杂任务可适当延长
4. **自动重试**: 网络错误/限流自动重试，最多 3 次，指数退避
5. **日志记录**: 每次调用记录 request_id、耗时、token 消耗
6. **降级策略**: 主模型不可用时自动切换轻量模型

```python
# 标准调用示例
from src.infrastructure.llm import LLMClient

client = LLMClient()

# 简单任务 — 使用轻量模型
result = client.call(
    prompt_template="review/compliance.j2",
    variables={"content": text, "rules": rules},
    model="small",        # 使用 LLM_SMALL_MODEL
    response_format="json"
)

# 复杂任务 — 使用主模型
result = client.call(
    prompt_template="content/copywriting.j2",
    variables={"topic": topic, "platform": "douyin", "tone": "professional"},
    model="main",          # 使用 LLM_MODEL
    timeout=120
)
```

### 3.4 常用操作

```bash
# 测试 LLM 连接
python scripts/test_llm.py

# 测试指定模型
python scripts/test_llm.py --model gpt-4o-mini

# 测试特定 Prompt 模板
python scripts/test_llm.py --template review/compliance.j2

# 查看 Token 使用统计
python scripts/llm_usage_stats.py

# 查看最近 100 次调用日志
tail -100 logs/llm_calls.log

# 验证 Prompt 模板语法
python scripts/validate_prompts.py

# 列出所有可用模板
python scripts/list_prompts.py
```

### 3.5 调试清单

- [ ] API Key 是否有效: `python scripts/test_llm.py` 应返回成功
- [ ] 网络可达性: `curl -s -o /dev/null -w "%{http_code}" $LLM_BASE_URL/models` 应返回 200
- [ ] 模型名称是否正确: 确认 `LLM_MODEL` 和 `LLM_SMALL_MODEL` 在目标 API 中存在
- [ ] Prompt 模板语法: `python scripts/validate_prompts.py` 无报错
- [ ] Token 用量是否异常: `python scripts/llm_usage_stats.py` 检查无突增
- [ ] 重试逻辑是否正常: 检查日志中无无限重试或过早放弃
- [ ] JSON 解析是否正常: 检查日志中无 `JSONDecodeError`

---

## 4. 浏览器自动化

### 4.1 配置参考

**主配置文件**: `config/settings.yaml` → `browser` 节点

```yaml
browser:
  headless: true                 # 无头模式
  timeout: 30                    # 页面加载超时 (秒)
  max_concurrent: 1              # 最大并发浏览器实例
  stealth_mode: true             # 反检测模式
  viewport:
    width: 1920
    height: 1080
  user_agent: "Mozilla/5.0 ..."  # 自定义 UA (stealth_mode 时自动生成)
  proxy: null                    # 代理设置 (可选)
  slow_mo: 0                     # 操作间隔毫秒数 (调试用)
  screenshot_on_error: true      # 出错时自动截图
```

### 4.2 平台脚本

每个平台的自动化脚本位于 `src/infrastructure/browser/platform/`：

| 文件 | 平台 | 主要功能 |
|------|------|---------|
| `douyin.py` | 抖音 | 登录、发布视频、查看数据、评论管理 |
| `xiaohongshu.py` | 小红书 | 登录、发布笔记、数据采集、互动管理 |
| `bilibili.py` | Bilibili | 登录、投稿、弹幕/评论管理、数据查看 |
| `twitter.py` | Twitter/X | 登录、发推、趋势采集、互动数据 |

**通用基类**: `src/infrastructure/browser/base.py` — 封装 Playwright 通用操作（反检测、Cookie 管理、截图等）。

### 4.3 会话存储

浏览器登录状态（Cookie、LocalStorage）持久化存储在：

```
data/browser_profiles/
├── douyin/
│   └── state.json          # 抖音登录状态
├── xiaohongshu/
│   └── state.json          # 小红书登录状态
├── bilibili/
│   └── state.json          # B站登录状态
└── twitter/
    └── state.json          # Twitter 登录状态
```

### 4.4 常用操作

```bash
# 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium

# 手动登录并保存状态（交互式）
python scripts/browser_login.py --platform douyin

# 验证登录状态是否有效
python scripts/browser_login.py --platform douyin --check

# 测试页面可访问性
python scripts/browser_test.py --platform xiaohongshu --url "https://creator.xiaohongshu.com"

# 手动操作浏览器（调试模式，可见窗口）
python scripts/browser_debug.py --platform bilibili --no-headless

# 清理指定平台的登录状态
rm data/browser_profiles/douyin/state.json

# 查看浏览器运行日志
tail -f logs/browser.log
```

### 4.5 调试清单

- [ ] Playwright 是否安装: `playwright --version` 应正常输出版本号
- [ ] Chromium 浏览器是否安装: `playwright install --dry-run chromium` 确认已安装
- [ ] 登录状态是否有效:
  ```bash
  python scripts/browser_login.py --platform douyin --check
  python scripts/browser_login.py --platform xiaohongshu --check
  python scripts/browser_login.py --platform bilibili --check
  python scripts/browser_login.py --platform twitter --check
  ```
- [ ] 目标页面是否可访问: 使用 `browser_test.py` 检查关键 URL
- [ ] 反检测是否生效: 检查 `stealth_mode: true`，日志中无 "bot detected" 错误
- [ ] 并发限制是否正常: `max_concurrent: 1` 时不应有多个浏览器同时运行
- [ ] 截图目录是否存在: `ls data/screenshots/` 确认错误截图正常生成
- [ ] 代理配置（如有）是否生效: 检查请求是否通过代理

---

## 5. 媒体处理

### 5.1 配置参考

**主配置文件**: `config/settings.yaml` → `media` 节点

```yaml
media:
  ffmpeg_path: ffmpeg              # FFmpeg 可执行文件路径
  imagemagick_path: convert        # ImageMagick 路径 (可选)
  image_quality: 85                # 图片输出质量 (1-100)
  video_bitrate: 2M                # 视频默认码率
  video_codec: h264                # 视频编码格式
  audio_bitrate: 192k              # 音频默认码率
  audio_codec: aac                 # 音频编码格式
  subtitle_font: "Microsoft YaHei" # 字幕默认字体
  tts:
    enabled: true
    provider: edge_tts             # TTS 服务提供商
    voice: zh-CN-XiaoxiaoNeural    # 默认语音
    rate: "+0%"                    # 语速调整
  temp_dir: data/files/temp/media  # 媒体处理临时目录
```

### 5.2 功能概览

| 类别 | 功能 | 对应工具 | 模块引用 |
|------|------|---------|---------|
| **图片** | 裁剪 | Pillow / FFmpeg | M-01, M-07 |
| | 缩放 | Pillow | M-01, M-07 |
| | 合成 (叠加水印/Logo) | Pillow | M-07 |
| | 格式转换 | Pillow | M-01 |
| | 调色/滤镜 | Pillow | M-07 |
| **视频** | 拼接/合并 | FFmpeg | M-09 |
| | 剪辑 (trim/cut) | FFmpeg | M-09 |
| | 文字转语音 (TTS) | edge_tts / Azure TTS | M-09 |
| | 添加字幕 | FFmpeg subtitles filter | M-09 |
| | 添加背景音乐 | FFmpeg amix filter | M-09 |
| | 格式转换/压缩 | FFmpeg | M-09 |
| **音频** | 提取 (从视频) | FFmpeg | M-03 |
| | 混音 | FFmpeg | M-09 |
| | 格式转换 | FFmpeg | M-03 |
| | 降噪 | FFmpeg afftdn filter | M-03 |

### 5.3 常用操作

```bash
# 检查 FFmpeg 是否可用
ffmpeg -version

# 检查 Pillow 是否安装
python -c "from PIL import Image; print(Image.__version__)"

# 图片处理示例
python scripts/media_process.py image --action resize --width 1080 --height 1920 --input input.png --output output.png
python scripts/media_process.py image --action composite --base bg.png --overlay logo.png --position "bottom-right"

# 视频处理示例
python scripts/media_process.py video --action trim --start 00:00:05 --duration 30 --input raw.mp4 --output trimmed.mp4
python scripts/media_process.py video --action concat --inputs part1.mp4 part2.mp4 --output merged.mp4

# TTS 文字转语音
python scripts/media_process.py tts --text "欢迎收看本期内容" --voice zh-CN-XiaoxiaoNeural --output narration.mp3

# 添加字幕到视频
python scripts/media_process.py video --action subtitle --input video.mp4 --srt subtitles.srt --output final.mp4

# 批量处理
python scripts/media_process.py batch --config batch_config.yaml

# 清理媒体临时文件
rm -rf data/files/temp/media/*
```

### 5.4 调试清单

- [ ] FFmpeg 是否安装:
  ```bash
  ffmpeg -version 2>&1 | head -1
  ```
- [ ] Pillow 是否安装:
  ```bash
  python -c "from PIL import Image; print('Pillow', Image.__version__)"
  ```
- [ ] TTS 服务是否可用:
  ```bash
  python -c "import edge_tts; print('edge_tts available')"
  ```
- [ ] 媒体临时目录是否存在且可写:
  ```bash
  mkdir -p data/files/temp/media && touch data/files/temp/media/write_test && rm data/files/temp/media/write_test
  ```
- [ ] 图片质量参数是否合理: `image_quality: 85` (过高浪费存储，过低影响画质)
- [ ] 视频码率是否合理: `video_bitrate: 2M` (根据平台要求调整，抖音推荐 2-4M)
- [ ] 中文字体是否可用: `fc-list :lang=zh | head -5`

---

## 6. API 路由

### 6.1 路由文件

所有 API 路由按模块组织在 `src/api/v1/` 目录：

| 文件 | 对应模块 | URL 前缀 | 主要端点 |
|------|---------|---------|---------|
| `material.py` | 素材库 | `/api/v1/materials` | CRUD 素材、标签管理、版本管理 |
| `content.py` | 内容工厂 | `/api/v1/content` | 创建内容、生成脚本、资产管理 |
| `review.py` | 审核系统 | `/api/v1/review` | 提交审核、查看结果、规则管理 |
| `distribute.py` | 分发引擎 | `/api/v1/distribute` | 发布任务、账号管理、发布记录 |
| `analytics.py` | 数据分析 | `/api/v1/analytics` | 数据查询、报告生成、仪表盘 |
| `learning.py` | 学习进化 | `/api/v1/learning` | 学习会话、策略更新、A/B 测试 |

### 6.2 中间件

中间件位于 `src/api/middleware/`：

| 文件 | 功能 | 说明 |
|------|------|------|
| `auth.py` | 认证中间件 | API Key / JWT 验证，白名单管理 |
| `logging.py` | 日志中间件 | 请求/响应日志，耗时统计 |
| `error_handler.py` | 错误处理 | 全局异常捕获，统一错误响应格式 |
| `cors.py` | 跨域处理 | CORS 配置，允许的来源和方法 |

### 6.3 应用入口

主入口文件 `src/main.py` 使用 FastAPI 应用工厂模式：

```python
# src/main.py 结构概览
from fastapi import FastAPI
from src.api.middleware import setup_middleware
from src.api.v1 import router as v1_router

def create_app() -> FastAPI:
    app = FastAPI(title="Hermes API", version="1.0.0")
    setup_middleware(app)
    app.include_router(v1_router, prefix="/api/v1")
    return app

app = create_app()
```

### 6.4 常用操作

```bash
# 启动开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 指定配置文件启动
uvicorn src.main:app --reload --port 8000 --env-file .env.dev

# 生产环境启动 (多 worker)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 访问 Swagger 文档
# 浏览器打开: http://localhost:8000/docs

# 访问 ReDoc 文档
# 浏览器打开: http://localhost:8000/redoc

# 健康检查
curl http://localhost:8000/health

# 测试特定端点
curl -X GET http://localhost:8000/api/v1/materials/ -H "Authorization: Bearer $API_KEY"

# 导出 OpenAPI 规范
python -c "from src.main import app; import json; print(json.dumps(app.openapi()))" > openapi.json
```

### 6.5 调试清单

- [ ] 开发服务器能否正常启动:
  ```bash
  uvicorn src.main:app --reload --port 8000
  ```
- [ ] Swagger 文档是否可访问: `http://localhost:8000/docs` 页面正常加载
- [ ] 健康检查端点是否响应:
  ```bash
  curl -s http://localhost:8000/health | python -m json.tool
  ```
- [ ] 认证中间件是否生效: 不带 Token 的请求应返回 401
- [ ] CORS 配置是否正确: 从不同源发起请求应正常返回
- [ ] 错误处理中间件是否生效: 触发异常应返回统一 JSON 格式错误
- [ ] 所有路由是否注册: `http://localhost:8000/docs` 中确认 6 个模块的路由全部出现
- [ ] 请求日志是否输出: 检查控制台/日志文件中包含请求信息

---

## 7. 任务调度

### 7.1 配置参考

**后端**: Celery + Redis (可选，开发环境可直接使用 APScheduler)

**主配置文件**: `config/settings.yaml` → `scheduler` 节点

```yaml
scheduler:
  backend: celery                    # celery | apscheduler
  broker_url: redis://localhost:6379/0  # Celery Broker
  result_backend: redis://localhost:6379/0
  timezone: Asia/Shanghai
  beat_schedule:                     # 定时任务配置
    daily_data_collection:
      task: tasks.collect_daily_data
      schedule: "0 2 * * *"         # 每天 02:00
    account_health_check:
      task: tasks.check_account_health
      schedule: "0 8 * * *"         # 每天 08:00
    hot_topic_tracker:
      task: tasks.track_hot_topics
      schedule: "0 */4 * * *"       # 每 4 小时
    weekly_report:
      task: tasks.generate_weekly_report
      schedule: "0 9 * * 1"         # 每周一 09:00
    rule_expiry_check:
      task: tasks.check_rule_expiry
      schedule: "0 3 * * *"         # 每天 03:00
    learning_report:
      task: tasks.generate_learning_report
      schedule: "0 10 * * 1"        # 每周一 10:00
```

### 7.2 定时任务一览

| 任务名称 | 调度时间 | 关联模块 | 说明 |
|---------|---------|---------|------|
| 每日数据采集 | 每天 02:00 | M-18 (分发引擎) | 采集各平台前一日发布数据 |
| 账号健康检查 | 每天 08:00 | M-19 (账号管理) | 检查各平台账号状态、粉丝变化 |
| 热点追踪 | 每 4 小时 | M-23 (热点追踪) | 抓取各平台热点话题/趋势 |
| 周报生成 | 每周一 09:00 | M-21 (周报) | 生成上周数据周报 |
| 规则时效检查 | 每天 03:00 | M-27 (数据分析) | 检查审核规则是否过期需更新 |
| 学习报告 | 每周一 10:00 | M-30 (学习报告) | 生成策略学习效果报告 |

### 7.3 常用操作

```bash
# 启动 Celery Worker
celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4

# 启动 Celery Beat (定时调度器)
celery -A src.tasks.celery_app beat --loglevel=info

# Worker + Beat 一起启动 (开发环境)
celery -A src.tasks.celery_app worker --beat --loglevel=info

# 查看注册的任务列表
celery -A src.tasks.celery_app inspect registered

# 查看活跃任务
celery -A src.tasks.celery_app inspect active

# 查看调度中的任务
celery -A src.tasks.celery_app inspect scheduled

# 手动触发指定任务
python scripts/trigger_task.py --task daily_data_collection

# 手动触发并查看结果
python scripts/trigger_task.py --task account_health_check --wait

# 查看任务执行历史
python scripts/task_history.py --days 7

# 查看 Flower 监控面板 (需安装 flower)
celery -A src.tasks.celery_app flower --port=5555
# 浏览器打开: http://localhost:5555

# 检查 Redis 是否运行
redis-cli ping
```

### 7.4 调试清单

- [ ] Redis 是否运行:
  ```bash
  redis-cli ping   # 应返回 PONG
  ```
- [ ] Celery Worker 是否正常启动:
  ```bash
  celery -A src.tasks.celery_app worker --loglevel=info
  ```
  Worker 启动后应显示 `ready` 状态
- [ ] Celery Beat 是否正常调度:
  ```bash
  celery -A src.tasks.celery_app beat --loglevel=info
  ```
  应看到 `Scheduler: Sending due task ...` 日志
- [ ] 时区是否为 Asia/Shanghai:
  ```bash
  python -c "from src.config import settings; print(settings.scheduler.timezone)"
  ```
- [ ] 定时任务配置是否正确: 对照 7.2 节的任务表检查 cron 表达式
- [ ] 任务执行是否成功: 查看 Celery 日志中无 `FAILURE` 状态
- [ ] Flower 监控是否可访问: `http://localhost:5555`
- [ ] 手动触发任务是否正常:
  ```bash
  python scripts/trigger_task.py --task daily_data_collection
  ```

---

## 8. 配置文件参考

### 8.1 主配置: `config/settings.yaml`

Hermes 全局配置文件，共 9 个顶级节点：

```yaml
# ===== 应用基础配置 =====
app:
  name: Hermes
  version: 1.0.0
  debug: false
  env: development            # development | staging | production
  log_level: INFO

# ===== 服务器配置 =====
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: false               # 生产环境必须为 false

# ===== 数据库配置 =====
database:
  url: sqlite:///data/db/social_auto_pilot.db
  echo: false
  pool_size: 5
  pool_recycle: 3600

# ===== 文件存储配置 =====
storage:
  base_path: data/files
  temp_path: data/files/temp
  max_upload: 524288000       # 500MB
  allowed_extensions:
    images: [jpg, jpeg, png, gif, webp, bmp]
    videos: [mp4, mov, avi, mkv, webm]
    audio: [mp3, wav, aac, flac, ogg]
    documents: [pdf, docx, xlsx, pptx, txt, json, csv]

# ===== LLM 配置 =====
llm:
  api_key: ${LLM_API_KEY}
  base_url: ${LLM_BASE_URL}
  model: gpt-4o
  small_model: gpt-4o-mini
  timeout: 60
  max_retries: 3
  temperature: 0.7

# ===== 浏览器自动化配置 =====
browser:
  headless: true
  timeout: 30
  max_concurrent: 1
  stealth_mode: true
  viewport:
    width: 1920
    height: 1080

# ===== 媒体处理配置 =====
media:
  ffmpeg_path: ffmpeg
  image_quality: 85
  video_bitrate: 2M
  tts:
    enabled: true
    provider: edge_tts
    voice: zh-CN-XiaoxiaoNeural

# ===== 任务调度配置 =====
scheduler:
  backend: celery
  broker_url: redis://localhost:6379/0
  timezone: Asia/Shanghai
  beat_schedule:
    daily_data_collection:
      task: tasks.collect_daily_data
      schedule: "0 2 * * *"
    # ... 其他定时任务

# ===== 日志配置 =====
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/hermes.log
  max_bytes: 104857600        # 100MB
  backup_count: 10
  separate_modules: true      # 每个模块单独日志文件
```

### 8.2 审核规则: `config/review_rules/compliance_rules.yaml`

内容合规审核规则配置：

```yaml
# ===== 敏感词库 =====
sensitive_words:
  categories:
    political:
      - 政治敏感词1
      - 政治敏感词2
    adult:
      - 成人内容词1
      - 成人内容词2
    violence:
      - 暴力内容词1
      - 暴力内容词2
    gambling:
      - 赌博相关词1
      - 赌博相关词2

# ===== 竞品名称 =====
competitor_names:
  platforms:
    - 竞品平台A
    - 竞品平台B
  products:
    - 竞品产品X
    - 竞品产品Y

# ===== 平台规则 =====
platform_rules:
  douyin:
    max_duration: 300          # 视频最长 5 分钟
    forbidden_categories:
      - 医疗健康
      - 金融理财
    title_max_length: 55
    description_max_length: 1000
  xiaohongshu:
    max_images: 18
    forbidden_hashtags:
      - 违禁标签1
    note_max_length: 1000
  bilibili:
    max_duration: 600          # 10 分钟
    danmaku_filter: true
    cover_ratio: "16:9"
  twitter:
    max_chars: 280
    media_limit: 4
    poll_max_duration: 604800  # 7 天
```

### 8.3 审核规则: `config/review_rules/default_rules.yaml`

默认审核规则（4 条）：

```yaml
rules:
  - id: R001
    name: 内容合规检查
    type: compliance
    priority: critical         # critical | high | medium | low
    enabled: true
    description: "检查内容是否包含敏感词、违禁内容、平台禁用类别"
    actions:
      on_fail: block           # block | warn | manual_review
    checks:
      - sensitive_words
      - platform_rules
      - forbidden_categories

  - id: R002
    name: 品牌一致性检查
    type: brand
    priority: high
    enabled: true
    description: "检查内容是否符合品牌调性、视觉规范、话术规范"
    actions:
      on_fail: manual_review
    checks:
      - tone_of_voice
      - visual_identity
      - brand_guidelines

  - id: R003
    name: 内容质量检查
    type: quality
    priority: high
    enabled: true
    description: "检查内容的原创度、信息准确性、格式规范"
    actions:
      on_fail: warn
    checks:
      - originality_score     # 原创度 > 80%
      - fact_check            # 事实核查
      - format_validation     # 格式校验

  - id: R004
    name: 竞品规避检查
    type: competition
    priority: medium
    enabled: true
    description: "检查是否提及竞品名称、是否包含竞品对比"
    actions:
      on_fail: manual_review
    checks:
      - competitor_mention
      - comparative_content
```

### 8.4 配置验证

```bash
# 验证 settings.yaml 语法
python scripts/validate_config.py --file config/settings.yaml

# 验证所有配置文件
python scripts/validate_config.py --all

# 查看当前生效的配置（敏感信息脱敏）
python scripts/show_config.py

# 查看指定节点的配置
python scripts/show_config.py --section database
python scripts/show_config.py --section llm

# 导出配置为环境变量格式
python scripts/export_config.py --format env > .env.example
```

### 8.5 配置调试清单

- [ ] `config/settings.yaml` 是否存在且 YAML 语法正确
- [ ] `config/review_rules/compliance_rules.yaml` 是否存在
- [ ] `config/review_rules/default_rules.yaml` 是否存在
- [ ] 所有 `${ENV_VAR}` 引用的环境变量是否已设置
- [ ] 各节点默认值是否合理（非生产环境 `debug` 不应为 `false` 等）
- [ ] 敏感信息（API Key、密码）是否通过环境变量注入，未硬编码在文件中
- [ ] `.gitignore` 中是否排除了含敏感信息的配置文件

---

## 附录 A: 快速启动检查脚本

将以下内容保存为 `scripts/health_check.sh`，一键检查所有基础设施：

```bash
#!/bin/bash
# Hermes 基础设施健康检查
echo "=== Hermes 基础设施健康检查 ==="
echo ""

# 1. 数据库
echo "[1/7] 检查数据库..."
if [ -f "data/db/social_auto_pilot.db" ]; then
    echo "  OK: 数据库文件存在"
else
    echo "  FAIL: 数据库文件不存在"
fi

# 2. 文件存储
echo "[2/7] 检查文件存储..."
for dir in data/files/materials/images data/files/materials/videos \
           data/files/outputs/images data/files/outputs/videos \
           data/files/reports/daily data/files/temp; do
    if [ -d "$dir" ] && [ -w "$dir" ]; then
        echo "  OK: $dir"
    else
        echo "  FAIL: $dir 不存在或不可写"
    fi
done

# 3. LLM
echo "[3/7] 检查 LLM..."
python scripts/test_llm.py --quiet && echo "  OK" || echo "  FAIL"

# 4. 浏览器
echo "[4/7] 检查浏览器..."
playwright --version > /dev/null 2>&1 && echo "  OK: Playwright" || echo "  FAIL: Playwright"

# 5. 媒体处理
echo "[5/7] 检查媒体处理..."
ffmpeg -version > /dev/null 2>&1 && echo "  OK: FFmpeg" || echo "  FAIL: FFmpeg"
python -c "from PIL import Image" 2>/dev/null && echo "  OK: Pillow" || echo "  FAIL: Pillow"

# 6. API
echo "[6/7] 检查 API..."
curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "  OK: API" || echo "  SKIP: API 未运行"

# 7. 任务调度
echo "[7/7] 检查任务调度..."
redis-cli ping > /dev/null 2>&1 && echo "  OK: Redis" || echo "  SKIP: Redis 未运行"

echo ""
echo "=== 检查完成 ==="
```

## 附录 B: 常用环境变量汇总

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DATABASE_URL` | 数据库连接串 | `sqlite:///data/db/social_auto_pilot.db` |
| `LLM_API_KEY` | LLM API 密钥 | 无 (必填) |
| `LLM_BASE_URL` | LLM API 端点 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 主模型 | `gpt-4o` |
| `LLM_SMALL_MODEL` | 轻量模型 | `gpt-4o-mini` |
| `REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |
| `APP_ENV` | 运行环境 | `development` |
| `APP_DEBUG` | 调试模式 | `false` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

> **文档维护**: 当基础设施配置发生变更时，请同步更新本文档。
> **最后更新**: 2026-07-12
