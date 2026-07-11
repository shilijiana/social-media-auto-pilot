# Hermes 智能体 — 调试指南

> **文档性质**：Hermes 系统的全链路调试手册，覆盖从环境搭建到 30 个模块的逐级调试策略。
> **目标受众**：Hermes Agent（AI 自动编码与集成调试）
> **最后更新**：2026-07-12
> **版本**：v1.0

---

## 目录

1. [调试前置条件](#1-调试前置条件)
2. [三阶段调试策略](#2-三阶段调试策略)
   - [2.1 P0 阶段（第1-4周）：人工主导 — 最小闭环](#21-p0-阶段第1-4周人工主导--最小闭环)
   - [2.2 P1 阶段（第5-12周）：人机协同 — 质量闭环](#22-p1-阶段第5-12周人机协同--质量闭环)
   - [2.3 P2 阶段（第13周起）：系统主导 — 智能闭环](#23-p2-阶段第13周起系统主导--智能闭环)
3. [按闭环流程的调试顺序](#3-按闭环流程的调试顺序)
   - [3.1 闭环一：素材采集](#31-闭环一素材采集)
   - [3.2 闭环二：内容生产](#32-闭环二内容生产)
   - [3.3 闭环三：审阅管理](#33-闭环三审阅管理)
   - [3.4 闭环四：分发采集](#34-闭环四分发采集)
   - [3.5 闭环五：数据分析](#35-闭环五数据分析)
   - [3.6 闭环六：自学习](#36-闭环六自学习)
4. [模块间接口对接调试](#4-模块间接口对接调试)
5. [验收标准总表](#5-验收标准总表)
6. [常见问题排查](#6-常见问题排查)
7. [调试命令速查](#7-调试命令速查)

---

## 1. 调试前置条件

### 1.1 环境要求

| 依赖项 | 最低版本 | 验证命令 |
|--------|---------|----------|
| Python | 3.11+ | `python --version` |
| pip | 23.0+ | `pip --version` |
| FFmpeg | 5.0+ | `ffmpeg -version` |
| Playwright | 1.40+ | `playwright --version` |
| Redis（生产） | 6.0+ | `redis-cli ping` |
| Git | 2.30+ | `git --version` |

### 1.2 虚拟环境与依赖安装

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

# 3. 升级 pip
pip install --upgrade pip

# 4. 安装项目依赖（开发模式）
pip install -e ".[dev]"

# 5. 安装基础依赖包
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

### 1.3 数据库初始化

```bash
# 完整初始化（创建所有表）
python scripts/init_db.py

# 验证数据库是否创建成功
ls -la data/db/social_auto_pilot.db

# 查看所有已创建的表
python scripts/show_schema.py

# 验证数据库连接
python -c "from src.infrastructure.database import engine; engine.connect(); print('数据库连接成功')"

# 如有迁移需求
alembic upgrade head
alembic history
```

### 1.4 LLM API Key 配置

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，填写以下必填项：
# LLM_API_KEY=sk-your-api-key-here
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o
# LLM_SMALL_MODEL=gpt-4o-mini

# 3. 验证环境变量是否加载
source .env
echo $LLM_API_KEY | head -c 10
echo "... (已设置)"

# 4. 测试 LLM 连接
python scripts/test_llm.py
```

### 1.5 浏览器驱动安装

```bash
# 安装 Chromium 浏览器及系统依赖
playwright install chromium
playwright install-deps chromium

# 验证安装
playwright install --dry-run chromium

# 测试浏览器能否正常启动
python scripts/browser_test.py --quick

# 手动登录各平台并保存会话状态
python scripts/browser_login.py --platform douyin
python scripts/browser_login.py --platform xiaohongshu
python scripts/browser_login.py --platform bilibili
python scripts/browser_login.py --platform twitter

# 验证登录状态
python scripts/browser_login.py --platform douyin --check
```

### 1.6 FFmpeg 配置

```bash
# 确认 FFmpeg 在系统 PATH 中
which ffmpeg
ffmpeg -version | head -1

# 如未安装（Ubuntu/Debian）
sudo apt-get update && sudo apt-get install -y ffmpeg

# 验证编解码器支持
ffmpeg -codecs | grep -E "h264|aac|libx264"

# 验证 Pillow 图片库
python -c "from PIL import Image; print('Pillow', Image.__version__)"

# 验证 edge_tts
python -c "import edge_tts; print('edge_tts available')"

# 创建媒体临时目录
mkdir -p data/files/temp/media
```

### 1.7 配置验证清单

在开始调试之前，请逐一确认以下项目：

- [ ] Python 版本 ≥ 3.11：`python --version` 输出确认
- [ ] 虚拟环境已激活：终端提示符显示 `(.venv)`
- [ ] 所有依赖包已安装：`pip list | wc -l` 输出 > 40
- [ ] 数据库文件存在：`ls -la data/db/social_auto_pilot.db`
- [ ] 数据库所有表已创建：`python scripts/show_schema.py` 无报错
- [ ] LLM_API_KEY 已配置：`echo $LLM_API_KEY` 不为空
- [ ] LLM 连接测试通过：`python scripts/test_llm.py` 返回成功
- [ ] Playwright Chromium 已安装：`playwright install --dry-run chromium` 显示已安装
- [ ] FFmpeg 可执行：`ffmpeg -version` 正常输出
- [ ] 文件存储目录已创建：`data/files/` 下所有子目录存在
- [ ] 文件存储目录可写：`touch data/files/temp/write_test && rm data/files/temp/write_test`
- [ ] 浏览器登录状态已保存：`ls data/browser_profiles/*/state.json` 存在
- [ ] 配置文件 YAML 语法正确：`python scripts/validate_config.py --all`
- [ ] 日志目录存在：`ls -d logs/`
- [ ] Redis 可用（如需要）：`redis-cli ping` 返回 PONG
- [ ] 磁盘剩余空间 > 2GB：`df -h data/files/ | tail -1 | awk '{print $4}'`

---

## 2. 三阶段调试策略

### 2.1 P0 阶段（第1-4周）：人工主导 — 最小闭环

#### 2.1.1 阶段目标

打通 **素材采集 → 内容生产 → 分发采集** 的最短闭环。此阶段人工深度参与，系统在每个关键节点需人工确认后才能继续。

#### 2.1.2 模块范围

M-02、M-03、M-07、M-08、M-09、M-10、M-11、M-16、M-17、M-18（共 10 个模块）

#### 2.1.3 调试顺序与步骤

**必须严格按照以下顺序进行，前一个模块验收通过后方可开始下一个模块的调试。**

---

##### 步骤 1：M-02 图文素材采集

**目标**：从指定平台（抖音/小红书/B站/X）采集图文类素材并入库。

**前置依赖**：无（本闭环起点）

**调试命令**：

```bash
# 单模块调试 — 采集抖音图文素材
python -m src.tasks.material.collect_images \
  --platform douyin \
  --keyword "人工智能" \
  --max-items 10 \
  --output data/files/materials/images/

# 采集小红书图文素材
python -m src.tasks.material.collect_images \
  --platform xiaohongshu \
  --keyword "科技" \
  --max-items 10

# 验证采集结果
python -m src.tasks.material.collect_images \
  --platform douyin \
  --keyword "人工智能" \
  --max-items 10 \
  --dry-run

# 检查入库数据
python -c "
from src.models.material import Material
from src.infrastructure.database import SessionLocal
db = SessionLocal()
count = db.query(Material).filter(Material.type == 'image').count()
print(f'图文素材入库总数: {count}')
db.close()
"

# 验证素材 JSON 格式
python scripts/validate_material_json.py --type image --limit 5
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 素材采集成功 | 检查 `data/files/materials/images/` 目录 | 至少采集到 1 个有效图片文件 |
| 素材元数据入库 | 查询 `materials` 表 | 采集的每条素材都有对应数据库记录 |
| material_id 格式正确 | 检查 ID 匹配 `^MAT-\d{4}-\d{6}$` | 所有素材 ID 格式合规 |
| 图片分辨率记录 | 检查 `resolution` 字段 | width/height 不为空且 > 0 |
| 版权状态标记 | 检查 `copyright_status` 字段 | 值为枚举值之一 |
| 清晰度评分 | 检查 `clarity_score` 字段 | 0-100 之间 |
| 文件命名规范 | 检查文件名格式 | 符合 `[选题编号]_M02_[平台]_v[版本]_[日期].[扩展名]` |
| 错误处理 | 模拟网络中断 | 系统记录错误日志，不崩溃 |

---

##### 步骤 2：M-03 视频素材采集

**目标**：从指定平台采集视频类素材并入库。

**前置依赖**：M-02 已通过（共享素材采集基础设施）

**调试命令**：

```bash
# 单模块调试 — 采集抖音视频素材
python -m src.tasks.material.collect_videos \
  --platform douyin \
  --keyword "AI" \
  --max-items 5 \
  --output data/files/materials/videos/

# 采集B站视频素材
python -m src.tasks.material.collect_videos \
  --platform bilibili \
  --keyword "技术" \
  --max-items 5

# 验证视频采集结果
python -m src.tasks.material.collect_videos \
  --platform douyin \
  --keyword "AI" \
  --max-items 5 \
  --dry-run

# 检查入库数据
python -c "
from src.models.material import Material
from src.infrastructure.database import SessionLocal
db = SessionLocal()
videos = db.query(Material).filter(Material.type == 'video').all()
for v in videos[:5]:
    print(f'{v.material_id}: {v.path}, {v.duration}s, {v.resolution}')
db.close()
"

# 验证视频格式和元数据
python scripts/validate_material_json.py --type video --limit 5
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 视频素材采集成功 | 检查 `data/files/materials/videos/` 目录 | 至少采集到 1 个有效视频文件 |
| 视频时长记录 | 检查 `duration` 字段 | > 0 秒 |
| 视频分辨率记录 | 检查 `resolution` 字段 | width/height 不为空 |
| 缩略图生成 | 检查 `thumbnail_path` 字段 | 不为空且对应文件存在 |
| 素材元数据入库 | 查询 `materials` 表 | 每条视频素材有对应记录 |
| 素材来源平台标记 | 检查 `platform` 字段 | 值为 `douyin`/`xiaohongshu`/`bilibili`/`twitter` 之一 |

---

##### 步骤 3：M-07 素材匹配与调用

**目标**：根据选题计划和平台要求，从素材库中匹配合适的素材组合。

**前置依赖**：M-02、M-03 已通过（需要素材库中有数据）

**调试命令**：

```bash
# 创建测试选题
python scripts/create_test_topic.py \
  --topic "AI技术趋势" \
  --platform douyin \
  --keywords "AI,人工智能,大模型"

# 执行素材匹配
python -m src.tasks.content.match_materials \
  --topic-id T2026-001 \
  --platform douyin \
  --min-count 3 \
  --max-count 10

# 查看匹配结果
python -m src.tasks.content.match_materials \
  --topic-id T2026-001 \
  --platform douyin \
  --verbose

# 验证匹配结果 JSON 格式
python scripts/validate_content_json.py --stage match --topic-id T2026-001
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 素材匹配返回结果 | 执行匹配命令 | 返回 ≥ 3 条匹配素材 |
| 匹配相关性 | 检查匹配日志中的 `relevance_score` | 前 3 条 ≥ 0.5 |
| 素材类型覆盖 | 检查返回结果中的 `type` 字段 | 同时包含 image 和 video（如果素材库有） |
| 版权过滤 | 检查返回结果中的 `copyright_status` | 不包含 `expired` 状态素材 |
| 清晰度排序 | 检查结果列表顺序 | 按 `clarity_score` 降序排列 |
| 去重检查 | 检查返回的 material_id 列表 | 无重复 ID |
| 返回 JSON 格式合规 | 检查 JSON Schema | 符合 Content（partial）定义 |

---

##### 步骤 4：M-08 文案差异化生成

**目标**：基于匹配的素材和选题信息，为不同平台生成差异化文案。

**前置依赖**：M-07 已通过（需要素材匹配结果）

**调试命令**：

```bash
# 为抖音生成文案
python -m src.tasks.content.generate_copy \
  --topic-id T2026-001 \
  --platform douyin \
  --style professional \
  --output data/files/outputs/copywriting/

# 为小红书生成文案
python -m src.tasks.content.generate_copy \
  --topic-id T2026-001 \
  --platform xiaohongshu \
  --style friendly

# 为B站生成文案
python -m src.tasks.content.generate_copy \
  --topic-id T2026-001 \
  --platform bilibili \
  --style technical

# 验证多平台差异化
python -m src.tasks.content.generate_copy \
  --topic-id T2026-001 \
  --all-platforms \
  --compare

# 检查文案生成结果
python scripts/validate_content_json.py --stage copy --topic-id T2026-001
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 文案成功生成 | 检查输出目录 | 每个平台生成至少 1 份文案文件 |
| 多平台差异化 | 对比各平台文案 | 不同平台的文案存在明显差异（非简单复制） |
| 文案包含标签 | 检查 `tags` 字段 | `minItems: 1`，至少 1 个标签 |
| content_id 格式 | 检查 ID 匹配 `^CTN-\d{4}-\d{6}$` | 所有内容 ID 格式合规 |
| 平台适配 | 检查 `platform` 字段 | 与请求的平台一致 |
| LLM 调用正常 | 检查 `logs/llm_calls.log` | 无 `JSONDecodeError` 或超时 |
| 文案字数合规 | 检查文案长度 | 抖音 ≤ 1000 字，小红书 ≤ 1000 字，B站无限制，X ≤ 280 字符 |

---

##### 步骤 5：M-09 封面图生成

**目标**：根据文案内容和匹配的素材生成封面图。

**前置依赖**：M-08 已通过（需要文案内容）

**调试命令**：

```bash
# 为指定内容生成封面图
python -m src.tasks.content.generate_cover \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --style modern \
  --output data/files/outputs/images/

# 批量生成封面图
python -m src.tasks.content.generate_cover \
  --topic-id T2026-001 \
  --all-platforms

# 验证封面图
python scripts/validate_image.py \
  --file data/files/outputs/images/CTN-2026-000001_cover.png \
  --min-width 1080 \
  --min-height 1920

# 检查封面图记录
python -c "
from src.models.content import CoverImage
from src.infrastructure.database import SessionLocal
db = SessionLocal()
covers = db.query(CoverImage).filter(CoverImage.content_id == 'CTN-2026-000001').all()
for c in covers:
    print(f'{c.content_id}: {c.path}, {c.width}x{c.height}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 封面图成功生成 | 检查输出目录 | 文件存在且大小 > 10KB |
| 图片尺寸符合平台要求 | 检查图片属性 | 抖音 1080x1920，B站 1920x1080 |
| 图片格式正确 | `file` 命令检查 | PNG 或 JPEG |
| 图片质量 | 检查 `image_quality` | 清晰无模糊、水印位置正确 |
| 封面图与内容关联 | 检查 `cover_images` 表 | content_id 匹配 |
| 文字可读性 | 人工目视检查 | 文字清晰、与背景对比度足够 |

---

##### 步骤 6：M-10 视频初剪

**目标**：基于匹配的视频素材进行初步剪辑（拼接、裁剪、转场）。

**前置依赖**：M-07 已通过（需要视频素材匹配结果）

**调试命令**：

```bash
# 视频初剪（单条）
python -m src.tasks.content.rough_cut \
  --topic-id T2026-001 \
  --platform douyin \
  --max-duration 60 \
  --output data/files/outputs/videos/

# 视频初剪（B站长视频）
python -m src.tasks.content.rough_cut \
  --topic-id T2026-001 \
  --platform bilibili \
  --max-duration 300

# 检查视频草稿
python scripts/validate_video.py \
  --file data/files/outputs/videos/T2026-001_M10_douyin_v1_20260712.mp4 \
  --check-codec h264

# 验证视频草稿记录
python -c "
from src.models.content import VideoDraft
from src.infrastructure.database import SessionLocal
db = SessionLocal()
drafts = db.query(VideoDraft).filter(VideoDraft.topic_id == 'T2026-001').all()
for d in drafts:
    print(f'{d.content_id}: {d.path}, {d.duration}s, {d.platform}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 视频草稿成功生成 | 检查输出目录 | 文件存在且大小 > 100KB |
| 视频时长符合要求 | `ffprobe` 检查 | 抖音 ≤ 300s，B站 ≤ 600s |
| 视频编码正确 | `ffprobe -v error -select_streams v:0 -show_entries stream=codec_name` | h264 |
| 音频编码正确 | `ffprobe -v error -select_streams a:0 -show_entries stream=codec_name` | aac |
| 视频可正常播放 | `ffplay` 或浏览器打开 | 无花屏、无卡顿 |
| 转场过渡正常 | 人工目视检查 | 转场处无黑帧、无跳帧 |
| 视频草稿入库 | 检查 `video_drafts` 表 | 有对应记录 |

---

##### 步骤 7：M-11 内容精加工与定稿

**目标**：将文案、封面图、视频草稿整合为最终内容，进行精加工（字幕、背景音乐、调色等）。

**前置依赖**：M-08、M-09、M-10 已通过

**调试命令**：

```bash
# 内容精加工（单条）
python -m src.tasks.content.finalize \
  --content-id CTN-2026-000001 \
  --add-subtitle \
  --add-bgm data/assets/bgm/tech_loop.mp3 \
  --output data/files/outputs/videos/

# 查看内容最终状态
python -m src.tasks.content.finalize \
  --content-id CTN-2026-000001 \
  --status

# 验证内容 JSON
python scripts/validate_content_json.py --stage finalize --content-id CTN-2026-000001

# 查看定稿内容详情
python -c "
from src.models.content import Content
from src.infrastructure.database import SessionLocal
db = SessionLocal()
content = db.query(Content).filter(Content.content_id == 'CTN-2026-000001').first()
if content:
    print(f'ID: {content.content_id}')
    print(f'状态: {content.status}')
    print(f'封面: {content.cover_path}')
    print(f'视频: {content.video_path}')
    print(f'标签: {content.tags}')
    print(f'引用素材: {content.material_refs}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 内容整合成功 | 检查输出文件 | 视频文件包含字幕和 BGM |
| 字幕同步准确 | 人工检查字幕时间轴 | 字幕与语音匹配，偏移 < 0.5s |
| 背景音乐混音 | 检查音频轨道 | BGM 音量不盖过人声 |
| 内容状态正确 | 检查 `status` 字段 | 值为 `draft` |
| 素材引用完整 | 检查 `material_refs` 字段 | 包含所有使用的素材 ID |
| 版本号正确 | 检查 `version` 字段 | 首次定稿为 `v1` |
| JSON Schema 合规 | 验证脚本检查 | 符合 Content 完整定义 |

---

##### 步骤 8：M-16 多平台分发

**目标**：将定稿内容发布到指定平台。

**前置依赖**：M-11 已通过（需要定稿内容）

**调试命令**：

```bash
# 发布到单个平台（Dry Run 模式，不实际发布）
python -m src.tasks.distribute.publish \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --dry-run

# 发布到所有目标平台（Dry Run）
python -m src.tasks.distribute.publish \
  --content-id CTN-2026-000001 \
  --all-platforms \
  --dry-run

# 正式发布到抖音
python -m src.tasks.distribute.publish \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --scheduled-at "2026-07-12T20:00:00+08:00"

# 查看发布任务状态
python -m src.tasks.distribute.publish \
  --content-id CTN-2026-000001 \
  --list-tasks

# 检查发布任务记录
python -c "
from src.models.distribute import PublishTask
from src.infrastructure.database import SessionLocal
db = SessionLocal()
tasks = db.query(PublishTask).filter(PublishTask.content_id == 'CTN-2026-000001').all()
for t in tasks:
    print(f'{t.task_id}: {t.platform}, {t.status}, {t.scheduled_at}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| Dry Run 不实际发布 | 执行 dry-run 后检查平台 | 平台上无新内容 |
| 发布任务创建成功 | 检查 `publish_tasks` 表 | 有对应记录，status 为 `queued` |
| 发布任务 ID 格式 | 检查 `task_id` 格式 | 匹配 `^PUB-\d{4}-\d{6}$` |
| 定时发布 | 检查 `scheduled_at` 字段 | 值正确且含时区 |
| 平台登录状态有效 | 发布前自动检查 | 不抛出 `LoginExpiredError` |
| 多平台并行分发 | 同时发布到多个平台 | 各平台独立执行，互不影响 |
| 失败重试机制 | 模拟网络中断 | 自动重试，最多 3 次 |

---

##### 步骤 9：M-17 发布状态监控与应急响应

**目标**：监控发布任务状态，处理发布失败、平台审核等异常情况。

**前置依赖**：M-16 已通过（需要有发布任务）

**调试命令**：

```bash
# 检查所有待处理发布任务
python -m src.tasks.distribute.monitor_status \
  --all

# 检查特定内容发布状态
python -m src.tasks.distribute.monitor_status \
  --content-id CTN-2026-000001

# 重试失败任务
python -m src.tasks.distribute.monitor_status \
  --retry-failed \
  --max-retries 3

# 撤回发布
python -m src.tasks.distribute.monitor_status \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --withdraw

# 查看发布日志
python -m src.tasks.distribute.monitor_status \
  --content-id CTN-2026-000001 \
  --show-logs

# 验证状态流转
python scripts/validate_status_transition.py \
  --content-id CTN-2026-000001 \
  --expected-status published
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 状态轮询正常 | 执行监控命令 | 返回各任务当前状态 |
| 状态变更检测 | 模拟状态变更 | 检测到并记录变更日志 |
| 发布失败检测 | 模拟发布失败 | 自动标记为 `failed` 并记录错误信息 |
| 重试逻辑 | 触发重试 | 按退避策略重试，retry_count 递增 |
| 撤回功能 | 执行撤回 | status 变为 `withdrawn` |
| 平台审核状态 | 检查 `under_review` 状态 | 正确识别平台审核中状态 |
| 发布日志完整 | 检查 `publish_logs` 表 | 每条状态变更都有日志记录 |

---

##### 步骤 10：M-18 效果数据采集

**目标**：从各平台采集已发布内容的效果数据（播放量、点赞、评论等）。

**前置依赖**：M-16、M-17 已通过（需要已发布内容）

**调试命令**：

```bash
# 采集指定内容效果数据
python -m src.tasks.distribute.collect_performance \
  --content-id CTN-2026-000001 \
  --platform douyin

# 采集所有平台效果数据
python -m src.tasks.distribute.collect_performance \
  --content-id CTN-2026-000001 \
  --all-platforms

# 按采集节点采集（24h/72h/7d/30d）
python -m src.tasks.distribute.collect_performance \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --node 24h

# 查看效果数据
python -m src.tasks.distribute.collect_performance \
  --content-id CTN-2026-000001 \
  --platform douyin \
  --show

# 验证效果数据 JSON
python scripts/validate_performance_json.py \
  --content-id CTN-2026-000001

# 检查效果数据记录
python -c "
from src.models.distribute import PerformanceMetric
from src.infrastructure.database import SessionLocal
db = SessionLocal()
metrics = db.query(PerformanceMetric).filter(
    PerformanceMetric.content_id == 'CTN-2026-000001'
).all()
for m in metrics:
    print(f'{m.content_id} @ {m.collection_node}: views={m.views}, likes={m.likes}, engagement={m.engagement_rate}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 效果数据采集成功 | 执行采集命令 | 返回非零指标数据 |
| 关键指标完整 | 检查返回 JSON | 包含 views/likes/comments/shares |
| 采集节点标记 | 检查 `collection_node` | 值为 `24h`/`72h`/`7d`/`30d` 之一 |
| 数据入库 | 检查 `performance_metrics` 表 | 有对应记录 |
| 互动率计算 | 检查 `engagement_rate` | 值 = (likes+comments+shares)/views |
| 完播率 | 检查 `completion_rate` | 0-1 之间（视频类内容） |
| 时间戳含时区 | 检查 `collected_at` | ISO 8601 含 +08:00 |

---

#### 2.1.4 P0 阶段验收标准

| 验收项 | 通过条件 |
|--------|---------|
| 素材采集 | 能从至少 1 个平台采集 ≥ 10 条素材并入库 |
| 素材匹配 | 能根据选题从素材库匹配 ≥ 3 条相关素材 |
| 文案生成 | 能为至少 2 个平台生成差异化文案 |
| 封面图生成 | 能生成符合平台尺寸要求的封面图 |
| 视频初剪 | 能输出可播放的视频草稿文件 |
| 内容定稿 | 能整合文案+封面+视频为完整内容 |
| 多平台分发 | 能在至少 1 个平台成功发布内容（含 Dry Run） |
| 状态监控 | 能轮询并更新发布状态 |
| 效果采集 | 能采集已发布内容的播放量等关键指标 |
| 全链路 | 从素材采集到效果采集完整链路可走通 |

---

### 2.2 P1 阶段（第5-12周）：人机协同 — 质量闭环

#### 2.2.1 阶段目标

在 P0 基础上增加质量管控（合规自检、分级审阅）、账号安全监控和初步自学习能力。系统可自主完成部分质检，异常情况提升至人工处理。

#### 2.2.2 模块范围

M-05、M-06、M-12、M-13、M-14、M-19、M-22、M-25、M-26（共 9 个模块）

#### 2.2.3 调试顺序

**必须严格按照以下顺序进行调试。**

---

##### 步骤 1：M-05 素材去重与质量控制

**目标**：对采集的素材进行去重处理和质量评分筛选。

**前置依赖**：M-02、M-03 已通过

**调试命令**：

```bash
# 素材去重
python -m src.tasks.material.deduplicate \
  --all

# 指定相似度阈值去重
python -m src.tasks.material.deduplicate \
  --similarity-threshold 0.9

# 质量评分
python -m src.tasks.material.quality_score \
  --all \
  --min-score 60

# 查看去重统计
python -m src.tasks.material.deduplicate \
  --stats

# 验证去重效果
python scripts/validate_dedup.py --check-duplicates
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 相似素材检测 | 检查去重日志 | 识别出相似度 > 0.9 的素材对 |
| 去重处理 | 检查数据库 | 重复素材被标记，主素材保留 |
| 质量评分 | 检查 `quality_score` 字段 | 每个素材都有 0-100 的评分 |
| 低质量过滤 | 检查过滤结果 | 评分 < 60 的素材被标记为低质量 |
| 去重不误删 | 人工抽查 | 没有内容不同但被误判为重复的素材 |

---

##### 步骤 2：M-06 素材入库与版权追踪

**目标**：完善素材入库流程，增加标签管理和版权状态追踪。

**前置依赖**：M-05 已通过

**调试命令**：

```bash
# 素材入库（完整流程）
python -m src.tasks.material.ingest \
  --dir data/files/materials/images/ \
  --auto-tag

# 版权检查
python -m src.tasks.material.copyright_check \
  --material-id MAT-2026-000001

# 批量版权检查
python -m src.tasks.material.copyright_check \
  --all \
  --check-expiring

# 标签管理
python -m src.tasks.material.manage_tags \
  --material-id MAT-2026-000001 \
  --add-tags "科技,AI,教程"

# 查看版权到期提醒
python -m src.tasks.material.copyright_check \
  --expiring-within 30

# 验证入库完整性
python scripts/validate_material_ingest.py --material-id MAT-2026-000001
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 素材入库完整 | 检查 `materials` 表 | 所有必要字段已填充 |
| 自动标签生成 | 检查 `material_tags` 表 | 入库素材自动关联标签 |
| 版权状态标记 | 检查 `copyright_status` | 不为 `unknown` |
| 版权到期预警 | 检查版权检查输出 | 30天内到期的素材被列出 |
| 授权到期日记录 | 检查 `license_expiry` | licensed/expiring 状态的素材有到期日 |

---

##### 步骤 3：M-12 合规性自检

**目标**：在内容定稿后自动进行合规检查（敏感词、广告法、版权素材、平台规则）。

**前置依赖**：M-11 已通过

**调试命令**：

```bash
# 执行合规检查
python -m src.tasks.content.compliance_check \
  --content-id CTN-2026-000001

# 查看检查结果
python -m src.tasks.content.compliance_check \
  --content-id CTN-2026-000001 \
  --show-details

# 批量合规检查
python -m src.tasks.content.compliance_check \
  --status draft \
  --all

# 验证合规报告
python scripts/validate_compliance_json.py \
  --content-id CTN-2026-000001

# 检查合规检查记录
python -c "
from src.models.content import ComplianceCheck
from src.infrastructure.database import SessionLocal
db = SessionLocal()
checks = db.query(ComplianceCheck).filter(
    ComplianceCheck.content_id == 'CTN-2026-000001'
).all()
for c in checks:
    print(f'{c.check_id}: passed={c.overall_passed}, items={len(c.check_items)}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 敏感词检测 | 测试含敏感词的文案 | 被正确识别并标记 |
| 广告法合规 | 测试含"最""第一"等词汇 | 被检测并给出修改建议 |
| 版权素材检查 | 检查素材引用 | 所有引用素材版权状态被验证 |
| 平台规则检查 | 对不同平台分别检查 | 按平台规则逐项检查 |
| 检查结果 JSON | 验证 JSON Schema | 符合 ComplianceResult 定义 |
| check_id 格式 | 检查 ID 格式 | 匹配 `^CHK-\d{4}-\d{6}$` |
| 内容状态更新 | 检查 content status | 合规通过 → `compliance_passed`，不通过 → `compliance_failed` |

---

##### 步骤 4：M-13 分级审阅引擎

**目标**：实现 A/B/C 三级审阅模式，支持多节点审阅链。

**前置依赖**：M-11、M-12 已通过

**调试命令**：

```bash
# 创建审阅任务
python -m src.tasks.review.create_task \
  --content-id CTN-2026-000001 \
  --mode B

# 查看审阅任务
python -m src.tasks.review.create_task \
  --content-id CTN-2026-000001 \
  --show

# 模拟审阅流程
python -m src.tasks.review.simulate \
  --task-id REV-2026-000001 \
  --outcome approved

# 添加审阅意见
python -m src.tasks.review.add_comment \
  --task-id REV-2026-000001 \
  --position "第1段" \
  --type must_fix \
  --content "开篇需要更有吸引力"

# 验证审阅任务 JSON
python scripts/validate_review_json.py --task-id REV-2026-000001

# 检查审阅任务记录
python -c "
from src.models.review import ReviewTask
from src.infrastructure.database import SessionLocal
db = SessionLocal()
task = db.query(ReviewTask).filter(ReviewTask.task_id == 'REV-2026-000001').first()
if task:
    print(f'任务: {task.task_id}')
    print(f'模式: {task.review_mode}')
    print(f'状态: {task.status}')
    print(f'审阅节点: {len(task.review_nodes)}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 审阅任务创建 | 检查 `review_tasks` 表 | 有对应记录 |
| 三级审阅模式 | 分别测试 A/B/C 模式 | 各模式审阅流程不同 |
| A 模式严格审阅 | 测试 A 模式 | 全部检查项被执行 |
| B 模式标准审阅 | 测试 B 模式 | 重点检查项被执行 |
| C 模式快速审阅 | 测试 C 模式 | 仅合规检查被执行 |
| 审阅意见管理 | 添加/查看审阅意见 | 意见正确记录并可查询 |
| 状态流转 | 模拟审阅流程 | pending_review → in_review → approved/rejected/needs_revision |

---

##### 步骤 5：M-14 版本变更管理

**目标**：追踪内容的版本变更历史，支持版本回退和变更对比。

**前置依赖**：M-13 已通过

**调试命令**：

```bash
# 查看内容版本历史
python -m src.tasks.review.version_history \
  --content-id CTN-2026-000001

# 版本对比
python -m src.tasks.review.version_history \
  --content-id CTN-2026-000001 \
  --diff v1 v2

# 版本回退（Dry Run）
python -m src.tasks.review.version_history \
  --content-id CTN-2026-000001 \
  --rollback v1 \
  --dry-run

# 创建新版本
python -m src.tasks.review.version_history \
  --content-id CTN-2026-000001 \
  --create-version

# 检查版本记录
python -c "
from src.models.review import ContentVersion
from src.infrastructure.database import SessionLocal
db = SessionLocal()
versions = db.query(ContentVersion).filter(
    ContentVersion.content_id == 'CTN-2026-000001'
).order_by(ContentVersion.version).all()
for v in versions:
    print(f'版本 {v.version}: {v.created_at}, 变更: {v.change_summary}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 版本记录完整 | 检查 `content_versions` 表 | 每次变更都有版本记录 |
| 版本号递增 | 检查版本号序列 | v1 → v2 → v3 顺序递增 |
| 变更摘要记录 | 检查 `change_summary` | 每次变更都有摘要描述 |
| 版本对比 | 执行 diff 命令 | 能显示两个版本之间的差异 |
| 版本回退 | 执行回退 | 内容恢复到指定版本 |

---

##### 步骤 6：M-19 账号健康度监控

**目标**：监控各平台账号状态（封禁风险、限流、粉丝变化等）。

**前置依赖**：M-16、M-17 已通过

**调试命令**：

```bash
# 检查所有平台账号健康度
python -m src.tasks.distribute.account_health \
  --all

# 检查指定平台
python -m src.tasks.distribute.account_health \
  --platform douyin

# 查看健康度历史
python -m src.tasks.distribute.account_health \
  --platform douyin \
  --history 7

# 检查异常告警
python -m src.tasks.distribute.account_health \
  --check-alerts

# 检查账号健康记录
python -c "
from src.models.distribute import AccountHealth
from src.infrastructure.database import SessionLocal
db = SessionLocal()
health = db.query(AccountHealth).filter(
    AccountHealth.platform == 'douyin'
).order_by(AccountHealth.checked_at.desc()).first()
if health:
    print(f'平台: {health.platform}')
    print(f'状态: {health.status}')
    print(f'粉丝数: {health.followers}')
    print(f'限流状态: {health.rate_limited}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 账号状态检查 | 执行健康检查 | 返回各平台账号状态 |
| 粉丝变化追踪 | 检查粉丝数据 | 记录粉丝增减 |
| 限流检测 | 检查 `rate_limited` 字段 | 正确识别限流状态 |
| 异常告警 | 检查告警输出 | 异常状态产生告警通知 |
| 历史数据保留 | 检查 `account_health` 表 | 历史健康数据可追溯 |

---

##### 步骤 7：M-22 评论区语义挖掘与隐私脱敏

**目标**：分析评论内容的情感倾向、关键话题，并进行隐私信息脱敏处理。

**前置依赖**：M-18 已通过

**调试命令**：

```bash
# 采集并分析评论
python -m src.tasks.analytics.comment_analysis \
  --content-id CTN-2026-000001 \
  --platform douyin

# 评论情感分析
python -m src.tasks.analytics.comment_analysis \
  --content-id CTN-2026-000001 \
  --sentiment

# 评论隐私脱敏
python -m src.tasks.analytics.comment_analysis \
  --content-id CTN-2026-000001 \
  --desensitize

# 查看分析结果
python -m src.tasks.analytics.comment_analysis \
  --content-id CTN-2026-000001 \
  --show

# 验证分析结果
python scripts/validate_comment_analysis.py --content-id CTN-2026-000001
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 评论采集 | 检查采集结果 | 采集到至少 1 条评论 |
| 情感分类 | 检查 `sentiment` 字段 | 分为 positive/negative/neutral |
| 关键词提取 | 检查分析输出 | 提取出评论中的关键话题 |
| 隐私脱敏 | 检查脱敏后的评论 | 手机号、邮箱等被替换为 *** |
| 分析结果入库 | 检查 `comment_analysis` 表 | 有对应记录 |

---

##### 步骤 8：M-25 学习数据收集

**目标**：从审阅过程和发布效果中收集学习数据。

**前置依赖**：M-13、M-18 已通过

**调试命令**：

```bash
# 收集学习数据
python -m src.tasks.learning.collect_data \
  --from-date 2026-07-01 \
  --to-date 2026-07-12

# 按事件类型收集
python -m src.tasks.learning.collect_data \
  --event-type revision_applied

# 查看收集统计
python -m src.tasks.learning.collect_data \
  --stats

# 检查学习记录
python -c "
from src.models.learning import LearningRecord
from src.infrastructure.database import SessionLocal
db = SessionLocal()
records = db.query(LearningRecord).limit(10).all()
for r in records:
    print(f'{r.record_id}: {r.event_type}, content={r.content_id}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 学习数据收集 | 执行收集命令 | 返回收集到的记录数 |
| 事件类型覆盖 | 检查 event_type 分布 | 包含 revision_applied/revision_ignored 等 |
| 数据关联正确 | 检查 content_id/review_task_id | 关联到正确的内容和审阅任务 |
| 记录 ID 格式 | 检查 record_id 格式 | 匹配 `^LRN-\d{4}-\d{6}$` |

---

##### 步骤 9：M-26 偏好提炼与规则生成

**目标**：从学习数据中提炼运营偏好和内容规则。

**前置依赖**：M-25 已通过

**调试命令**：

```bash
# 提炼偏好规则
python -m src.tasks.learning.extract_rules \
  --from-date 2026-07-01 \
  --min-confidence 60

# 按偏好类型提炼
python -m src.tasks.learning.extract_rules \
  --preference-type content

# 查看规则列表
python -m src.tasks.learning.extract_rules \
  --list

# 验证规则 JSON
python scripts/validate_rule_json.py --all

# 检查偏好规则记录
python -c "
from src.models.learning import PreferenceRule
from src.infrastructure.database import SessionLocal
db = SessionLocal()
rules = db.query(PreferenceRule).filter(PreferenceRule.status == 'active').all()
for r in rules:
    print(f'{r.rule_id}: [{r.preference_type}] {r.rule_content[:50]}... (置信度: {r.confidence})')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 规则提炼成功 | 执行提炼命令 | 生成 ≥ 1 条规则 |
| 规则置信度 | 检查 `confidence` 字段 | ≥ 60（min-confidence 阈值） |
| 规则类型分类 | 检查 `preference_type` | 值为 content/visual/strategy 之一 |
| 规则来源记录 | 检查 `sources` 字段 | 标明规则的数据来源 |
| 规则 ID 格式 | 检查 rule_id 格式 | 匹配 `^RUL-\d{4}-\d{6}$` |
| 规则权重 | 检查 `weight` 字段 | > 0 |

---

#### 2.2.4 P1 阶段验收标准

| 验收项 | 通过条件 |
|--------|---------|
| 素材去重 | 重复素材检出率 > 90% |
| 素材质量过滤 | 低质量素材（< 60分）被自动标记 |
| 版权追踪 | 所有素材有版权状态，到期素材有预警 |
| 合规自检 | 敏感词/广告法/版权三项检查全部执行 |
| 分级审阅 | A/B/C 三级审阅流程全部可走通 |
| 版本管理 | 内容版本可追溯、可对比、可回退 |
| 账号健康 | 各平台账号状态可监控，异常可告警 |
| 评论分析 | 评论情感分类准确率 > 80% |
| 学习数据收集 | 审阅和发布事件数据自动收集 |
| 偏好提炼 | 至少提炼出 5 条置信度 ≥ 60 的偏好规则 |

---

### 2.3 P2 阶段（第13周起）：系统主导 — 智能闭环

#### 2.3.1 阶段目标

实现数据分析驱动的策略优化和完整的自学习闭环。系统具备自我进化能力，人工干预比例降至最低。

#### 2.3.2 模块范围

M-01、M-04、M-15、M-20、M-21、M-23、M-24、M-27、M-28、M-29、M-30（共 11 个模块）

#### 2.3.3 调试顺序

---

##### 步骤 1：M-01 关键词智能扩展

**目标**：基于选题自动扩展相关关键词（同义词、相关词、长尾词）。

**前置依赖**：无（可独立调试）

**调试命令**：

```bash
# 关键词扩展
python -m src.tasks.material.expand_keywords \
  --keyword "人工智能" \
  --platform douyin

# 批量扩展
python -m src.tasks.material.expand_keywords \
  --keywords "人工智能,自动驾驶,元宇宙" \
  --all-platforms

# 查看扩展结果
python -m src.tasks.material.expand_keywords \
  --keyword "人工智能" \
  --show

# 验证关键词 JSON
python scripts/validate_keyword_json.py --keyword "人工智能"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 扩展词生成 | 执行扩展命令 | 每个原始词生成 ≥ 3 个扩展词 |
| 扩展类型覆盖 | 检查 type 字段 | 包含 synonym/related/long_tail |
| 关联度评分 | 检查 `relevance` 字段 | 0-1 之间，同义词 > 0.8 |
| 平台适配 | 对不同平台扩展 | 不同平台关键词有差异 |

---

##### 步骤 2：M-04 参考文案与竞品采集

**目标**：采集竞品内容和行业参考文案。

**前置依赖**：M-01 已通过（需要扩展关键词）

**调试命令**：

```bash
# 采集竞品内容
python -m src.tasks.material.collect_competitor \
  --platform douyin \
  --competitor-ids "user_123,user_456"

# 采集行业参考
python -m src.tasks.material.collect_competitor \
  --keyword "AI教程" \
  --platform xiaohongshu \
  --max-items 20

# 查看采集结果
python -m src.tasks.material.collect_competitor \
  --show-stats
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 竞品内容采集 | 执行采集命令 | 采集到指定竞品的内容 |
| 行业参考采集 | 按关键词采集 | 采集到相关参考内容 |
| 内容分类标记 | 检查采集结果 | 区分竞品内容和行业参考 |
| 采集频率控制 | 检查请求间隔 | 不触发平台频率限制 |

---

##### 步骤 3：M-15 通用素材池管理

**目标**：管理可复用的通用素材（品牌 Logo、常用 BGM、模板等）。

**前置依赖**：M-06 已通过

**调试命令**：

```bash
# 添加通用素材
python -m src.tasks.review.manage_common_materials \
  --add data/assets/logo.png \
  --type brand

# 查看通用素材池
python -m src.tasks.review.manage_common_materials \
  --list

# 按类型筛选
python -m src.tasks.review.manage_common_materials \
  --list \
  --type bgm

# 检查素材池
python -c "
from src.models.review import CommonMaterial
from src.infrastructure.database import SessionLocal
db = SessionLocal()
materials = db.query(CommonMaterial).all()
for m in materials:
    print(f'{m.material_id}: {m.type}, {m.path}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 素材添加 | 添加测试素材 | 成功入库并可查询 |
| 素材分类 | 按类型筛选 | 正确返回对应类型素材 |
| 素材引用计数 | 检查引用次数 | 记录每个素材被引用次数 |
| 素材过期管理 | 设置过期时间 | 过期素材被标记 |

---

##### 步骤 4：M-20 数据清洗与聚合

**目标**：清洗和聚合多平台、多时间节点的效果数据。

**前置依赖**：M-18 已通过

**调试命令**：

```bash
# 数据清洗
python -m src.tasks.analytics.clean_data \
  --from-date 2026-07-01 \
  --to-date 2026-07-12

# 数据聚合
python -m src.tasks.analytics.clean_data \
  --aggregate \
  --period weekly

# 查看清洗统计
python -m src.tasks.analytics.clean_data \
  --stats

# 检查分析报告记录
python -c "
from src.models.analytics import AnalyticsReport
from src.infrastructure.database import SessionLocal
db = SessionLocal()
reports = db.query(AnalyticsReport).limit(5).all()
for r in reports:
    print(f'{r.report_id}: {r.report_type}, {r.generated_at}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 数据清洗完成 | 执行清洗命令 | 无报错，输出清洗统计 |
| 异常数据过滤 | 检查清洗日志 | 异常值（如 views < 0）被过滤 |
| 数据聚合正确 | 检查聚合结果 | 多节点数据合并为周期数据 |
| 报告 ID 格式 | 检查 report_id 格式 | 匹配 `^RPT-\d{4}-\d{6}$` |

---

##### 步骤 5：M-21 多维度效果分析

**目标**：对清洗后的数据进行多维度分析（横向平台对比、纵向时间对比）。

**前置依赖**：M-20 已通过

**调试命令**：

```bash
# 执行多维度分析
python -m src.tasks.analytics.analyze \
  --period weekly \
  --from-date 2026-07-06 \
  --to-date 2026-07-12

# 横向对比（平台间）
python -m src.tasks.analytics.analyze \
  --comparison horizontal

# 纵向对比（时间维度）
python -m src.tasks.analytics.analyze \
  --comparison vertical

# 查看分析报告
python -m src.tasks.analytics.analyze \
  --report-id RPT-2026-000001 \
  --show
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 横向对比 | 检查 `horizontal_comparison` | 各平台数据正确对比 |
| 纵向对比 | 检查 `vertical_comparison` | 包含当前值、历史值和变化率 |
| 指标汇总 | 检查 `metrics_summary` | 包含 total_views/engagement_rate 等 |
| 分析报告 JSON | 验证 JSON Schema | 符合 AnalyticsReport 定义 |

---

##### 步骤 6：M-23 跨平台热点追踪

**目标**：追踪各平台热点话题和趋势。

**前置依赖**：无（可独立调试）

**调试命令**：

```bash
# 热点追踪
python -m src.tasks.analytics.track_hotspots \
  --platform douyin

# 全平台追踪
python -m src.tasks.analytics.track_hotspots \
  --all-platforms

# 查看热点
python -m src.tasks.analytics.track_hotspots \
  --show-top 20

# 检查热点记录
python -c "
from src.models.analytics import HotTopic
from src.infrastructure.database import SessionLocal
db = SessionLocal()
topics = db.query(HotTopic).order_by(HotTopic.heat_score.desc()).limit(10).all()
for t in topics:
    print(f'{t.platform}: {t.topic} (热度: {t.heat_score})')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 热点采集 | 执行追踪命令 | 各平台返回热点列表 |
| 热度评分 | 检查 `heat_score` | 0-100 之间 |
| 平台覆盖 | 检查各平台数据 | 每个平台都有热点数据 |
| 热点更新频率 | 定时任务执行 | 每 4 小时更新一次 |

---

##### 步骤 7：M-24 下期计划草案生成

**目标**：基于分析报告和热点追踪生成下期内容计划草案。

**前置依赖**：M-20、M-21、M-23 已通过

**调试命令**：

```bash
# 生成计划草案
python -m src.tasks.analytics.generate_plan \
  --from-date 2026-07-06 \
  --to-date 2026-07-12

# 查看计划草案
python -m src.tasks.analytics.generate_plan \
  --plan-id PLN-2026-000001 \
  --show

# 导出计划
python -m src.tasks.analytics.generate_plan \
  --plan-id PLN-2026-000001 \
  --export data/files/exports/
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 计划生成 | 执行生成命令 | 返回计划草案 |
| 选题建议 | 检查计划内容 | 包含基于热点的选题建议 |
| 发布时机建议 | 检查计划内容 | 包含基于数据分析的发布时机 |
| 策略调整建议 | 检查计划内容 | 包含基于效果数据的策略调整 |

---

##### 步骤 8：M-27 规则时效性管理

**目标**：管理偏好规则的时效性，自动降级或暂停过期规则。

**前置依赖**：M-26 已通过

**调试命令**：

```bash
# 检查规则时效
python -m src.tasks.learning.check_rule_expiry \
  --all

# 标记过期规则
python -m src.tasks.learning.check_rule_expiry \
  --auto-degrade

# 查看规则状态分布
python -m src.tasks.learning.check_rule_expiry \
  --stats
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 时效检查 | 执行检查命令 | 识别出过期/降级规则 |
| 自动降级 | 检查降级后的规则 | 过期规则 status 变为 `degraded` |
| 置信度衰减 | 检查长时间未验证的规则 | confidence 逐步下降 |

---

##### 步骤 9：M-28 初始偏好模板导入

**目标**：导入人工预设的偏好模板作为冷启动数据。

**前置依赖**：无（可独立调试）

**调试命令**：

```bash
# 导入偏好模板
python -m src.tasks.learning.import_templates \
  --file config/templates/preferences.yaml

# 查看已导入模板
python -m src.tasks.learning.import_templates \
  --list

# 验证模板数据
python -c "
from src.models.learning import PreferenceTemplate
from src.infrastructure.database import SessionLocal
db = SessionLocal()
templates = db.query(PreferenceTemplate).all()
print(f'已导入 {len(templates)} 个偏好模板')
for t in templates[:5]:
    print(f'  - {t.name}: {t.description}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 模板导入 | 执行导入命令 | 模板成功入库 |
| 模板格式 | 检查入库数据 | 所有必要字段完整 |
| 模板数量 | 检查导入统计 | ≥ 3 个模板 |

---

##### 步骤 10：M-29 学习成果应用

**目标**：将学习到的偏好规则应用到内容生产和分发环节。

**前置依赖**：M-26、M-27 已通过

**调试命令**：

```bash
# 应用学习规则到内容生产
python -m src.tasks.learning.apply_rules \
  --to content_generation

# 应用学习规则到分发策略
python -m src.tasks.learning.apply_rules \
  --to distribution

# 查看规则应用效果
python -m src.tasks.learning.apply_rules \
  --show-impact

# 检查规则应用记录
python -c "
from src.models.learning import PreferenceRule
from src.infrastructure.database import SessionLocal
db = SessionLocal()
rules = db.query(PreferenceRule).filter(
    PreferenceRule.status == 'active',
    PreferenceRule.applied_count > 0
).all()
for r in rules:
    print(f'{r.rule_id}: 应用 {r.applied_count} 次, 成功率 {r.success_rate:.2%}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 规则应用 | 检查应用日志 | 规则被正确注入内容生成流程 |
| 应用计数 | 检查 `applied_count` | 每次应用后计数递增 |
| 成功率追踪 | 检查 `success_rate` | 记录规则应用的成功率 |
| 内容质量改善 | 对比应用前后 | 应用规则后内容质量指标有提升 |

---

##### 步骤 11：M-30 学习成效量化与报告

**目标**：量化自学习系统的成效并生成报告。

**前置依赖**：M-29 已通过

**调试命令**：

```bash
# 生成学习报告
python -m src.tasks.learning.generate_report \
  --period weekly

# 查看学习报告
python -m src.tasks.learning.generate_report \
  --report-id RPT-2026-000050 \
  --show

# 导出学习报告
python -m src.tasks.learning.generate_report \
  --report-id RPT-2026-000050 \
  --export data/files/reports/weekly/

# 检查学习报告指标
python -c "
from src.models.learning import LearningReport
from src.infrastructure.database import SessionLocal
db = SessionLocal()
report = db.query(LearningReport).order_by(LearningReport.generated_at.desc()).first()
if report:
    print(f'人工修改率: {report.manual_revision_rate:.1%}')
    print(f'一次通过率: {report.first_pass_rate:.1%}')
    print(f'自动通过率: {report.auto_pass_rate:.1%}')
    print(f'平均审阅耗时: {report.avg_review_duration:.1f}分钟')
    print(f'新增规则数: {report.new_rules_count}')
    print(f'异常项数: {len(report.anomalies)}')
db.close()
"
```

**验收要点**：

| 验收项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 学习报告生成 | 执行报告命令 | 生成完整学习报告 |
| 人工修改率 | 检查 `manual_revision_rate` | 0-1 之间 |
| 一次通过率 | 检查 `first_pass_rate` | 0-1 之间 |
| 自动通过率 | 检查 `auto_pass_rate` | 0-1 之间 |
| 异常检测 | 检查 `anomalies` | 包含 confidence_drop/rule_conflict 等 |
| 置信度 Top10 | 检查 `top10_confidence` | 最多 10 条规则 |

---

#### 2.3.4 P2 阶段验收标准

| 验收项 | 通过条件 |
|--------|---------|
| 关键词扩展 | 每个选题自动扩展 ≥ 5 个有效关键词 |
| 竞品采集 | 自动采集并分类竞品内容 |
| 通用素材池 | 素材池管理功能完整 |
| 数据清洗 | 异常数据过滤率 > 95% |
| 多维度分析 | 横向和纵向分析报告生成正常 |
| 热点追踪 | 各平台热点每 4 小时更新 |
| 计划草案 | 基于数据自动生成下期计划 |
| 规则时效 | 过期规则自动降级 |
| 偏好模板 | 冷启动模板成功导入 |
| 学习成果应用 | 规则被实际应用到生产和分发 |
| 学习报告 | 成效量化指标完整，异常项可识别 |

---

## 3. 按闭环流程的调试顺序

### 3.1 闭环一：素材采集

**流程**：M-01 → M-02 / M-03 → M-04 → M-05 → M-06

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-01 关键词智能扩展 | 无 | `python -m src.tasks.material.expand_keywords --keyword "人工智能" --platform douyin` | 生成 ≥ 3 个扩展词，含 synonym/related/long_tail |
| 2 | M-02 图文素材采集 | M-01 | `python -m src.tasks.material.collect_images --platform douyin --keyword "人工智能" --max-items 10` | 采集 ≥ 1 个图片，元数据入库 |
| 3 | M-03 视频素材采集 | M-01 | `python -m src.tasks.material.collect_videos --platform douyin --keyword "AI" --max-items 5` | 采集 ≥ 1 个视频，含时长和缩略图 |
| 4 | M-04 参考文案与竞品采集 | M-01 | `python -m src.tasks.material.collect_competitor --platform douyin --keyword "AI教程" --max-items 20` | 采集到竞品和参考内容 |
| 5 | M-05 素材去重与质量控制 | M-02, M-03 | `python -m src.tasks.material.deduplicate --all` | 重复素材检出，质量评分完成 |
| 6 | M-06 素材入库与版权追踪 | M-05 | `python -m src.tasks.material.ingest --dir data/files/materials/images/ --auto-tag` | 版权状态标记，标签自动生成 |

---

### 3.2 闭环二：内容生产

**流程**：M-07 → M-08 → M-09 / M-10 → M-11 → M-12

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-07 素材匹配与调用 | M-02, M-03, M-06 | `python -m src.tasks.content.match_materials --topic-id T2026-001 --platform douyin --min-count 3` | 返回 ≥ 3 条匹配素材 |
| 2 | M-08 文案差异化生成 | M-07 | `python -m src.tasks.content.generate_copy --topic-id T2026-001 --platform douyin --style professional` | 生成文案，content_id 格式合规 |
| 3 | M-09 封面图生成 | M-08 | `python -m src.tasks.content.generate_cover --content-id CTN-2026-000001 --platform douyin --style modern` | 封面图尺寸符合平台要求 |
| 4 | M-10 视频初剪 | M-07 | `python -m src.tasks.content.rough_cut --topic-id T2026-001 --platform douyin --max-duration 60` | 视频可播放，编码正确 |
| 5 | M-11 内容精加工与定稿 | M-08, M-09, M-10 | `python -m src.tasks.content.finalize --content-id CTN-2026-000001 --add-subtitle --add-bgm bgm.mp3` | 字幕同步，BGM 混音正常 |
| 6 | M-12 合规性自检 | M-11 | `python -m src.tasks.content.compliance_check --content-id CTN-2026-000001` | 敏感词/广告法/版权三项检查完成 |

---

### 3.3 闭环三：审阅管理

**流程**：M-13 → M-14 / M-15

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-13 分级审阅引擎 | M-11, M-12 | `python -m src.tasks.review.create_task --content-id CTN-2026-000001 --mode B` | A/B/C 三级模式流程可走通 |
| 2 | M-14 版本变更管理 | M-13 | `python -m src.tasks.review.version_history --content-id CTN-2026-000001 --diff v1 v2` | 版本可追溯、可对比、可回退 |
| 3 | M-15 通用素材池管理 | M-06 | `python -m src.tasks.review.manage_common_materials --add data/assets/logo.png --type brand` | 素材池增删查改功能正常 |

---

### 3.4 闭环四：分发采集

**流程**：M-16 → M-17 → M-18 → M-19

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-16 多平台分发 | M-11, M-13 | `python -m src.tasks.distribute.publish --content-id CTN-2026-000001 --platform douyin --dry-run` | Dry Run 成功，发布任务创建 |
| 2 | M-17 发布状态监控与应急响应 | M-16 | `python -m src.tasks.distribute.monitor_status --content-id CTN-2026-000001` | 状态轮询正常，失败可重试 |
| 3 | M-18 效果数据采集 | M-16, M-17 | `python -m src.tasks.distribute.collect_performance --content-id CTN-2026-000001 --platform douyin` | 采集到关键指标数据 |
| 4 | M-19 账号健康度监控 | M-16, M-17 | `python -m src.tasks.distribute.account_health --platform douyin` | 账号状态可监控，异常可告警 |

---

### 3.5 闭环五：数据分析

**流程**：M-20 → M-21 → M-22 → M-23 → M-24

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-20 数据清洗与聚合 | M-18 | `python -m src.tasks.analytics.clean_data --from-date 2026-07-01 --to-date 2026-07-12` | 异常数据过滤，多节点聚合 |
| 2 | M-21 多维度效果分析 | M-20 | `python -m src.tasks.analytics.analyze --period weekly` | 横向和纵向对比完成 |
| 3 | M-22 评论区语义挖掘与隐私脱敏 | M-18 | `python -m src.tasks.analytics.comment_analysis --content-id CTN-2026-000001 --sentiment` | 情感分类正确，隐私已脱敏 |
| 4 | M-23 跨平台热点追踪 | 无 | `python -m src.tasks.analytics.track_hotspots --all-platforms` | 各平台热点数据采集 |
| 5 | M-24 下期计划草案生成 | M-20, M-21, M-22, M-23 | `python -m src.tasks.analytics.generate_plan --from-date 2026-07-06 --to-date 2026-07-12` | 计划草案包含选题和策略建议 |

---

### 3.6 闭环六：自学习

**流程**：M-25 → M-26 → M-27 → M-28 → M-29 → M-30

| 顺序 | 模块 | 上游依赖 | 单模块调试命令 | 验收要点 |
|------|------|---------|---------------|---------|
| 1 | M-25 学习数据收集 | M-13, M-18 | `python -m src.tasks.learning.collect_data --from-date 2026-07-01 --to-date 2026-07-12` | 审阅和发布事件数据收集 |
| 2 | M-26 偏好提炼与规则生成 | M-25 | `python -m src.tasks.learning.extract_rules --min-confidence 60` | 生成 ≥ 1 条置信度 ≥ 60 的规则 |
| 3 | M-27 规则时效性管理 | M-26 | `python -m src.tasks.learning.check_rule_expiry --all` | 过期规则自动降级 |
| 4 | M-28 初始偏好模板导入 | 无 | `python -m src.tasks.learning.import_templates --file config/templates/preferences.yaml` | 模板成功导入 ≥ 3 个 |
| 5 | M-29 学习成果应用 | M-26, M-27 | `python -m src.tasks.learning.apply_rules --to content_generation` | 规则被注入生产和分发 |
| 6 | M-30 学习成效量化与报告 | M-29 | `python -m src.tasks.learning.generate_report --period weekly` | 成效指标完整，异常可识别 |

---

## 4. 模块间接口对接调试

### 4.1 接口对接通用流程

当两个模块之间的接口需要调试时，按以下 5 步进行：

1. **确认数据格式**：查阅 [INTERFACE_CONTRACT.md](./INTERFACE_CONTRACT.md) 中对应接口的 JSON Schema 定义
2. **上游模块输出验证**：运行上游模块，导出输出 JSON，用 `python scripts/validate_json.py --schema <schema_name> --file <output.json>` 验证格式
3. **下游模块输入验证**：用上游输出作为下游模块的输入，验证下游模块能否正确解析
4. **端到端集成测试**：用 `python scripts/integration_test.py --from <module_a> --to <module_b>` 执行端到端测试
5. **错误场景覆盖**：测试异常输入（空数据、格式错误、缺失必填字段），确认下游模块有合理的错误处理

### 4.2 关键接口对接表

| 序号 | 上游模块 | 下游模块 | 传递数据 | 调试重点 |
|------|---------|---------|---------|---------|
| 1 | M-01 关键词智能扩展 | M-02 图文素材采集 | 扩展关键词列表（Keyword） | 关键词 JSON 格式正确性，platform 字段匹配 |
| 2 | M-01 关键词智能扩展 | M-03 视频素材采集 | 扩展关键词列表（Keyword） | 关键词 JSON 格式正确性，relevance 排序 |
| 3 | M-02 图文素材采集 | M-05 素材去重与质量控制 | 素材对象列表（Material[]） | material_id 唯一性，resolution 字段完整性 |
| 4 | M-03 视频素材采集 | M-05 素材去重与质量控制 | 素材对象列表（Material[]） | duration 字段不为空，thumbnail_path 有效性 |
| 5 | M-05 素材去重与质量控制 | M-06 素材入库与版权追踪 | 去重后的素材列表 | 去重标记正确，quality_score 范围 0-100 |
| 6 | M-06 素材入库与版权追踪 | M-07 素材匹配与调用 | 素材 ID 列表 + 版权状态 | copyright_status 不为 unknown，tags 非空 |
| 7 | M-07 素材匹配与调用 | M-08 文案差异化生成 | 匹配素材 + 选题信息（Content partial） | material_refs 完整，topic_id 关联正确 |
| 8 | M-07 素材匹配与调用 | M-10 视频初剪 | 匹配视频素材列表 | 视频素材的 path 可访问，duration 准确 |
| 9 | M-08 文案差异化生成 | M-11 内容精加工与定稿 | 文案草稿（Content） | copytext 非空，platform 与目标一致 |
| 10 | M-09 封面图生成 | M-11 内容精加工与定稿 | 封面图路径 | cover_path 文件存在，分辨率符合平台要求 |
| 11 | M-10 视频初剪 | M-11 内容精加工与定稿 | 视频草稿路径 | video_path 文件存在，编码为 h264 |
| 12 | M-12 合规性自检 | M-11 内容精加工与定稿 | 合规报告（ComplianceResult） | overall_passed 正确，不通过时有 suggestion |
| 13 | M-11 内容精加工与定稿 | M-13 分级审阅引擎 | 待审内容（ReviewTask） | content_id 关联，version 正确 |
| 14 | M-13 分级审阅引擎 | M-14 版本变更管理 | 审阅通过的版本数据 | version 号递增，变更摘要完整 |
| 15 | M-13 分级审阅引擎 | M-16 多平台分发 | 审阅通过的内容（Content） | status 为 review_approved |
| 16 | M-16 多平台分发 | M-17 发布状态监控与应急响应 | 发布任务（PublishTask） | task_id 格式，scheduled_at 含时区 |
| 17 | M-17 发布状态监控与应急响应 | M-18 效果数据采集 | 已发布内容的 platform_post_id | platform_post_id 非空 |
| 18 | M-18 效果数据采集 | M-20 数据清洗与聚合 | 效果数据（PerformanceData） | collection_node 正确，关键指标非空 |
| 19 | M-20 数据清洗与聚合 | M-21 多维度效果分析 | 清洗后的聚合数据 | 异常数据已过滤，聚合周期正确 |
| 20 | M-20/M-21/M-22/M-23 | M-24 下期计划草案生成 | 综合分析数据（AnalyticsReport） | suggestions 非空，hotspot_analysis 完整 |
| 21 | M-25 学习数据收集 | M-26 偏好提炼与规则生成 | 学习记录（LearningRecord） | event_type 分类正确，event_data 结构完整 |
| 22 | M-26 偏好提炼与规则生成 | M-29 学习成果应用 | 偏好规则（PreferenceRule） | status 为 active，confidence ≥ 阈值 |
| 23 | M-27 规则时效性管理 | M-29 学习成果应用 | 降级/过期规则通知 | degraded 规则被排除，active 规则保持 |
| 24 | M-29 学习成果应用 | M-30 学习成效量化与报告 | 规则应用效果数据 | applied_count 和 success_rate 准确 |

---

## 5. 验收标准总表

| 阶段 | 模块范围 | 核心验收项 | 通过条件 |
|------|---------|-----------|---------|
| P0 | M-02, M-03, M-07, M-08, M-09, M-10, M-11, M-16, M-17, M-18 | 全链路最小闭环 | 从素材采集到效果数据采集的完整链路可走通，每个模块的验收要点全部满足 |
| P0 | M-02, M-03 | 素材采集能力 | 至少 1 个平台可成功采集 ≥ 10 条素材，元数据完整入库 |
| P0 | M-07, M-08, M-09, M-10, M-11 | 内容生产能力 | 文案、封面图、视频草稿均成功生成并整合为完整内容 |
| P0 | M-16, M-17, M-18 | 分发采集能力 | 内容可在至少 1 个平台发布（含 Dry Run），状态可监控，效果数据可采集 |
| P1 | M-05, M-06, M-12, M-13, M-14, M-19, M-22, M-25, M-26 | 质量闭环 | 去重、版权、合规、审阅、版本、账号健康、学习数据收集全部功能可用 |
| P1 | M-05, M-06 | 素材质量管理 | 去重检出率 > 90%，版权状态标记率 100% |
| P1 | M-12, M-13, M-14 | 审阅管控 | A/B/C 三级审阅可走通，版本可追溯可回退 |
| P1 | M-25, M-26 | 初步自学习 | 学习数据可收集，≥ 5 条置信度 ≥ 60 的偏好规则被提炼 |
| P2 | M-01, M-04, M-15, M-20, M-21, M-23, M-24, M-27, M-28, M-29, M-30 | 智能闭环 | 数据驱动策略优化和完整自学习闭环可用 |
| P2 | M-01, M-04 | 智能采集 | 关键词自动扩展，竞品自动采集 |
| P2 | M-20, M-21, M-23, M-24 | 数据分析决策 | 多维度分析报告生成，热点追踪更新，计划草案自动生成 |
| P2 | M-27, M-28, M-29, M-30 | 自学习进化 | 规则时效自动管理，学习成果被应用，成效可量化报告 |

---

## 6. 常见问题排查

### 6.1 数据库问题

#### 问题 1：SQLite 数据库锁定（database is locked）

**症状**：
- 错误信息：`sqlite3.OperationalError: database is locked`
- 写入操作超时或失败
- 并发场景下频繁出现

**原因**：SQLite 不支持高并发写入，多个进程同时写入时会锁定。

**解决方案**：
```bash
# 1. 检查是否有其他进程在使用数据库
lsof data/db/social_auto_pilot.db

# 2. 开启 WAL 模式（允许并发读）
python -c "
from src.infrastructure.database import engine
with engine.connect() as conn:
    conn.execute('PRAGMA journal_mode=WAL;')
    print('WAL 模式已开启')
"

# 3. 增加超时时间（修改 config/settings.yaml）
# database:
#   connect_args:
#     timeout: 30

# 4. 生产环境切换到 PostgreSQL
# 修改 .env: DATABASE_URL=postgresql://user:pass@host:5432/hermes
```

#### 问题 2：数据库迁移失败（Alembic migration error）

**症状**：
- `alembic upgrade head` 报错
- 提示表已存在或列冲突

**原因**：迁移脚本与实际数据库状态不一致。

**解决方案**：
```bash
# 1. 查看当前迁移状态
alembic current

# 2. 查看迁移历史
alembic history

# 3. 回退到上一个版本
alembic downgrade -1

# 4. 如回退失败，检查迁移脚本
alembic check

# 5. 必要时重置数据库（仅开发环境）
python scripts/init_db.py --reset --confirm
alembic upgrade head
```

#### 问题 3：数据库文件损坏

**症状**：
- 查询返回异常结果或报 `database disk image is malformed`

**原因**：磁盘故障或进程异常终止。

**解决方案**：
```bash
# 1. 从备份恢复
cp data/db/backup_YYYYMMDD_HHMMSS.db data/db/social_auto_pilot.db

# 2. 如无备份，尝试修复
sqlite3 data/db/social_auto_pilot.db "PRAGMA integrity_check;"

# 3. 导出数据重建
sqlite3 data/db/social_auto_pilot.db .dump > dump.sql
# 删除原数据库文件后重新导入
sqlite3 data/db/social_auto_pilot.db < dump.sql
```

---

### 6.2 LLM 问题

#### 问题 4：API Key 无效或过期

**症状**：
- 错误：`401 Unauthorized` 或 `Incorrect API key provided`
- `python scripts/test_llm.py` 返回认证失败

**原因**：API Key 未设置、已过期或被吊销。

**解决方案**：
```bash
# 1. 检查环境变量
echo $LLM_API_KEY | head -c 15

# 2. 重新设置 API Key
export LLM_API_KEY=sk-your-new-key

# 3. 更新 .env 文件
# LLM_API_KEY=sk-your-new-key

# 4. 重新测试连接
source .env
python scripts/test_llm.py
```

#### 问题 5：LLM 返回格式不匹配（JSON 解析失败）

**症状**：
- 日志中出现 `JSONDecodeError`
- 下游模块无法解析 LLM 输出

**原因**：LLM 返回的不是合法 JSON，或字段与 Schema 不匹配。

**解决方案**：
```bash
# 1. 查看原始 LLM 响应
tail -50 logs/llm_calls.log | grep -A 5 "response"

# 2. 检查是否使用了 response_format 参数
# 确认代码中设置了 response_format="json_object"

# 3. 增加重试和容错逻辑
# 在 client.py 中添加 JSON 修复逻辑（如处理 markdown 代码块包裹）

# 4. 测试特定 Prompt 模板
python scripts/test_llm.py --template review/compliance.j2

# 5. 降低 temperature 提高输出稳定性
# llm.temperature: 0.3
```

#### 问题 6：LLM 请求超时

**症状**：
- 错误：`TimeoutError` 或 `ReadTimeout`
- 长时间等待后失败

**原因**：网络延迟、API 服务繁忙或模型响应慢。

**解决方案**：
```bash
# 1. 增加超时时间（config/settings.yaml）
# llm:
#   timeout: 120  # 从 60 增加到 120

# 2. 检查网络可达性
curl -s -o /dev/null -w "HTTP %{http_code}, Time: %{time_total}s\n" \
  $LLM_BASE_URL/models

# 3. 切换轻量模型处理简单任务
# 使用 model="small" 参数

# 4. 检查是否触发了速率限制
grep "rate_limit" logs/llm_calls.log
```

---

### 6.3 浏览器问题

#### 问题 7：Playwright 浏览器驱动版本不匹配

**症状**：
- 错误：`BrowserType.launch: Executable doesn't exist`
- 或 `Host system is missing dependencies`

**原因**：Chromium 未安装或版本与 playwright 不匹配。

**解决方案**：
```bash
# 1. 重新安装 Chromium
playwright install chromium --force

# 2. 安装系统依赖
playwright install-deps chromium

# 3. 验证安装
playwright install --dry-run chromium

# 4. 检查 playwright 版本
playwright --version

# 5. 手动指定浏览器路径（config/settings.yaml）
# browser:
#   executable_path: /usr/bin/chromium-browser
```

#### 问题 8：平台登录状态过期

**症状**：
- 发布或采集时提示"请先登录"
- 自动操作被重定向到登录页面

**原因**：浏览器保存的 Cookie/Session 已过期。

**解决方案**：
```bash
# 1. 检查登录状态
python scripts/browser_login.py --platform douyin --check

# 2. 重新登录（交互式，需人工扫码/输入验证码）
python scripts/browser_login.py --platform douyin

# 3. 清除过期状态后重新登录
rm data/browser_profiles/douyin/state.json
python scripts/browser_login.py --platform douyin

# 4. 如平台要求验证码，需开启可见窗口模式
python scripts/browser_login.py --platform douyin --no-headless
```

#### 问题 9：反检测失效导致操作被拦截

**症状**：
- 页面显示"检测到异常流量"或需要验证
- 元素定位失败或页面结构异常

**原因**：平台的反爬虫机制升级，stealth_mode 配置不足。

**解决方案**：
```bash
# 1. 确认 stealth_mode 已开启
python -c "from src.config import settings; print(settings.browser.stealth_mode)"

# 2. 增加操作间隔
# config/settings.yaml:
# browser:
#   slow_mo: 1000  # 操作间隔 1 秒

# 3. 使用真实 User-Agent
# browser:
#   user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ..."

# 4. 减少并发
# browser:
#   max_concurrent: 1

# 5. 检查是否有代理可用
# browser:
#   proxy: "http://proxy-host:port"
```

---

### 6.4 存储问题

#### 问题 10：磁盘空间不足

**症状**：
- 写入文件失败，错误 `No space left on device`
- 日志中频繁出现 `OSError: [Errno 28]`

**原因**：素材和产出文件占用大量磁盘空间。

**解决方案**：
```bash
# 1. 检查磁盘空间
df -h data/files/

# 2. 清理临时文件
python scripts/cleanup_temp.py
rm -rf data/files/temp/*

# 3. 查看各目录占用
du -sh data/files/materials/* data/files/outputs/* data/files/reports/*

# 4. 归档旧文件（超过 30 天的报告）
find data/files/reports/ -type f -mtime +30 -exec tar -rvf archive.tar {} \; -exec rm {} \;

# 5. 删除低质量素材
python -c "
from src.models.material import Material
from src.infrastructure.database import SessionLocal
db = SessionLocal()
low_quality = db.query(Material).filter(Material.clarity_score < 30).all()
print(f'低质量素材数: {len(low_quality)}')
# 谨慎删除，确认后再执行
"
```

#### 问题 11：文件权限问题

**症状**：
- 错误：`PermissionError: [Errno 13] Permission denied`
- 无法写入文件或创建目录

**原因**：运行进程的用户与文件所有者不一致。

**解决方案**：
```bash
# 1. 检查文件所有者
ls -la data/files/ data/db/

# 2. 修复权限
chmod -R 755 data/files/
chmod -R 755 data/db/
chmod 644 data/db/social_auto_pilot.db

# 3. 如使用 Docker，确保用户映射正确
# docker-compose.yml:
#   user: "1000:1000"

# 4. 确保目录存在
mkdir -p data/files/{materials/{images,videos,audio},outputs/{images,videos,copywriting},reports/{daily,weekly,monthly},exports,temp}
```

---

### 6.5 媒体处理问题

#### 问题 12：FFmpeg 未安装或不在 PATH 中

**症状**：
- 错误：`ffmpeg: command not found` 或 `FileNotFoundError: ffmpeg`
- 视频处理任务全部失败

**原因**：FFmpeg 未安装或未添加到系统 PATH。

**解决方案**：
```bash
# 1. 检查是否安装
which ffmpeg || echo "未找到 ffmpeg"

# 2. 安装 FFmpeg（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y ffmpeg

# 3. 安装 FFmpeg（CentOS/RHEL）
sudo yum install -y epel-release
sudo yum install -y ffmpeg

# 4. 安装 FFmpeg（macOS）
brew install ffmpeg

# 5. 手动指定路径（config/settings.yaml）
# media:
#   ffmpeg_path: /usr/local/bin/ffmpeg

# 6. 验证安装
ffmpeg -version | head -1
```

#### 问题 13：视频编解码器不支持

**症状**：
- 错误：`Unknown encoder 'libx264'` 或 `Decoder not found`
- 视频处理输出损坏或无法播放

**原因**：FFmpeg 编译时未包含所需编解码器。

**解决方案**：
```bash
# 1. 检查可用编解码器
ffmpeg -codecs | grep h264
ffmpeg -encoders | grep 264

# 2. 如缺少 h264 编码器，安装完整版
# Ubuntu/Debian
sudo apt-get install -y ffmpeg libavcodec-extra

# 3. 或使用备选编码器
# config/settings.yaml:
# media:
#   video_codec: libx264  # 改为 mpeg4 作为备选

# 4. 测试转码
ffmpeg -i test_input.mp4 -c:v libx264 -c:a aac test_output.mp4
```

#### 问题 14：中文字体缺失导致字幕乱码

**症状**：
- 视频字幕显示为方框或乱码
- 错误日志：`Cannot find font`

**原因**：系统缺少中文字体。

**解决方案**：
```bash
# 1. 检查可用中文字体
fc-list :lang=zh | head -5

# 2. 安装中文字体（Ubuntu/Debian）
sudo apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei

# 3. 安装中文字体（CentOS/RHEL）
sudo yum install -y wqy-zenhei-fonts wqy-microhei-fonts

# 4. 手动指定字体路径（config/settings.yaml）
# media:
#   subtitle_font: "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# 5. 刷新字体缓存
fc-cache -fv
```

---

### 6.6 通用调试技巧

#### 技巧 1：开启详细日志

```bash
# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG

# 或在 config/settings.yaml 中
# app:
#   log_level: DEBUG

# 查看实时日志
tail -f logs/hermes.log
tail -f logs/llm_calls.log
tail -f logs/browser.log
```

#### 技巧 2：模块隔离测试

```bash
# 使用 --dry-run 标志进行无副作用的测试
python -m src.tasks.distribute.publish --content-id CTN-2026-000001 --dry-run

# 使用测试数据库（不影响主数据库）
export DATABASE_URL=sqlite:///data/db/test_debug.db
python scripts/init_db.py
# 执行调试命令...
# 完成后删除测试数据库
rm data/db/test_debug.db
```

#### 技巧 3：手动验证数据格式

```bash
# 验证素材 JSON
python scripts/validate_json.py \
  --schema material \
  --file data/files/test_output.json

# 验证内容 JSON
python scripts/validate_json.py \
  --schema content \
  --file data/files/test_output.json

# 检查数据库记录
python -c "
from src.infrastructure.database import SessionLocal
from src.models.material import Material
db = SessionLocal()
materials = db.query(Material).limit(5).all()
import json
for m in materials:
    print(json.dumps({
        'id': m.material_id,
        'type': m.type,
        'copyright': m.copyright_status,
        'score': m.clarity_score
    }, ensure_ascii=False))
db.close()
"
```

---

## 7. 调试命令速查

### 7.1 环境检查

| 用途 | 命令 |
|------|------|
| Python 版本 | `python --version` |
| 依赖包列表 | `pip list` |
| 虚拟环境确认 | `which python`（应指向 .venv） |
| 配置文件验证 | `python scripts/validate_config.py --all` |
| 健康检查一键脚本 | `bash scripts/health_check.sh` |
| 查看当前配置 | `python scripts/show_config.py` |
| 查看指定配置节点 | `python scripts/show_config.py --section database` |

### 7.2 数据库

| 用途 | 命令 |
|------|------|
| 初始化数据库 | `python scripts/init_db.py` |
| 重置数据库 | `python scripts/init_db.py --reset --confirm` |
| 查看 Schema | `python scripts/show_schema.py` |
| 查看数据库统计 | `python scripts/db_stats.py` |
| 迁移升级 | `alembic upgrade head` |
| 迁移回退 | `alembic downgrade -1` |
| 查看迁移历史 | `alembic history` |
| 生成迁移脚本 | `alembic revision --autogenerate -m "描述"` |
| 备份数据库 | `cp data/db/social_auto_pilot.db data/db/backup_$(date +%Y%m%d_%H%M%S).db` |
| 测试连接 | `python -c "from src.infrastructure.database import engine; engine.connect(); print('OK')"` |

### 7.3 LLM

| 用途 | 命令 |
|------|------|
| 测试 LLM 连接 | `python scripts/test_llm.py` |
| 测试指定模型 | `python scripts/test_llm.py --model gpt-4o-mini` |
| 测试 Prompt 模板 | `python scripts/test_llm.py --template review/compliance.j2` |
| 查看 Token 用量 | `python scripts/llm_usage_stats.py` |
| 查看 LLM 调用日志 | `tail -100 logs/llm_calls.log` |
| 验证 Prompt 模板 | `python scripts/validate_prompts.py` |
| 列出所有模板 | `python scripts/list_prompts.py` |

### 7.4 浏览器

| 用途 | 命令 |
|------|------|
| 安装 Chromium | `playwright install chromium` |
| 安装系统依赖 | `playwright install-deps chromium` |
| 验证安装 | `playwright install --dry-run chromium` |
| 手动登录平台 | `python scripts/browser_login.py --platform <douyin/xiaohongshu/bilibili/twitter>` |
| 检查登录状态 | `python scripts/browser_login.py --platform <platform> --check` |
| 测试页面可访问性 | `python scripts/browser_test.py --platform <platform>` |
| 调试模式（可见窗口） | `python scripts/browser_debug.py --platform <platform> --no-headless` |
| 查看浏览器日志 | `tail -f logs/browser.log` |

### 7.5 媒体处理

| 用途 | 命令 |
|------|------|
| 检查 FFmpeg | `ffmpeg -version` |
| 检查编解码器 | `ffmpeg -codecs \| grep h264` |
| 图片处理 | `python scripts/media_process.py image --action resize --width 1080 --height 1920 --input in.png --output out.png` |
| 视频处理 | `python scripts/media_process.py video --action trim --start 00:00:05 --duration 30 --input raw.mp4 --output trimmed.mp4` |
| TTS 文字转语音 | `python scripts/media_process.py tts --text "测试文本" --output test.mp3` |
| 添加字幕 | `python scripts/media_process.py video --action subtitle --input video.mp4 --srt subs.srt --output final.mp4` |
| 检查 Pillow | `python -c "from PIL import Image; print(Image.__version__)"` |
| 验证视频文件 | `python scripts/validate_video.py --file video.mp4 --check-codec h264` |
| 验证图片文件 | `python scripts/validate_image.py --file image.png --min-width 1080` |

### 7.6 素材采集（闭环一）

| 用途 | 命令 |
|------|------|
| M-01 关键词扩展 | `python -m src.tasks.material.expand_keywords --keyword "人工智能" --platform douyin` |
| M-02 采集图文 | `python -m src.tasks.material.collect_images --platform douyin --keyword "AI" --max-items 10` |
| M-03 采集视频 | `python -m src.tasks.material.collect_videos --platform douyin --keyword "AI" --max-items 5` |
| M-04 采集竞品 | `python -m src.tasks.material.collect_competitor --platform douyin --keyword "AI教程" --max-items 20` |
| M-05 素材去重 | `python -m src.tasks.material.deduplicate --all` |
| M-05 质量评分 | `python -m src.tasks.material.quality_score --all --min-score 60` |
| M-06 素材入库 | `python -m src.tasks.material.ingest --dir data/files/materials/images/ --auto-tag` |
| M-06 版权检查 | `python -m src.tasks.material.copyright_check --all` |

### 7.7 内容生产（闭环二）

| 用途 | 命令 |
|------|------|
| M-07 素材匹配 | `python -m src.tasks.content.match_materials --topic-id T2026-001 --platform douyin --min-count 3` |
| M-08 文案生成 | `python -m src.tasks.content.generate_copy --topic-id T2026-001 --platform douyin --style professional` |
| M-09 封面图生成 | `python -m src.tasks.content.generate_cover --content-id CTN-2026-000001 --platform douyin` |
| M-10 视频初剪 | `python -m src.tasks.content.rough_cut --topic-id T2026-001 --platform douyin --max-duration 60` |
| M-11 内容定稿 | `python -m src.tasks.content.finalize --content-id CTN-2026-000001 --add-subtitle --add-bgm bgm.mp3` |
| M-12 合规检查 | `python -m src.tasks.content.compliance_check --content-id CTN-2026-000001` |

### 7.8 审阅管理（闭环三）

| 用途 | 命令 |
|------|------|
| M-13 创建审阅 | `python -m src.tasks.review.create_task --content-id CTN-2026-000001 --mode B` |
| M-13 模拟审阅 | `python -m src.tasks.review.simulate --task-id REV-2026-000001 --outcome approved` |
| M-14 版本历史 | `python -m src.tasks.review.version_history --content-id CTN-2026-000001` |
| M-14 版本对比 | `python -m src.tasks.review.version_history --content-id CTN-2026-000001 --diff v1 v2` |
| M-15 素材池管理 | `python -m src.tasks.review.manage_common_materials --add data/assets/logo.png --type brand` |

### 7.9 分发采集（闭环四）

| 用途 | 命令 |
|------|------|
| M-16 发布（Dry Run） | `python -m src.tasks.distribute.publish --content-id CTN-2026-000001 --platform douyin --dry-run` |
| M-16 定时发布 | `python -m src.tasks.distribute.publish --content-id CTN-2026-000001 --platform douyin --scheduled-at "2026-07-12T20:00:00+08:00"` |
| M-17 状态监控 | `python -m src.tasks.distribute.monitor_status --content-id CTN-2026-000001` |
| M-17 重试失败 | `python -m src.tasks.distribute.monitor_status --retry-failed --max-retries 3` |
| M-18 效果采集 | `python -m src.tasks.distribute.collect_performance --content-id CTN-2026-000001 --platform douyin` |
| M-19 账号健康 | `python -m src.tasks.distribute.account_health --platform douyin` |

### 7.10 数据分析（闭环五）

| 用途 | 命令 |
|------|------|
| M-20 数据清洗 | `python -m src.tasks.analytics.clean_data --from-date 2026-07-01 --to-date 2026-07-12` |
| M-21 多维度分析 | `python -m src.tasks.analytics.analyze --period weekly` |
| M-22 评论分析 | `python -m src.tasks.analytics.comment_analysis --content-id CTN-2026-000001 --sentiment` |
| M-23 热点追踪 | `python -m src.tasks.analytics.track_hotspots --all-platforms` |
| M-24 计划生成 | `python -m src.tasks.analytics.generate_plan --from-date 2026-07-06 --to-date 2026-07-12` |

### 7.11 自学习（闭环六）

| 用途 | 命令 |
|------|------|
| M-25 收集学习数据 | `python -m src.tasks.learning.collect_data --from-date 2026-07-01 --to-date 2026-07-12` |
| M-26 提炼规则 | `python -m src.tasks.learning.extract_rules --min-confidence 60` |
| M-27 检查时效 | `python -m src.tasks.learning.check_rule_expiry --all` |
| M-28 导入模板 | `python -m src.tasks.learning.import_templates --file config/templates/preferences.yaml` |
| M-29 应用规则 | `python -m src.tasks.learning.apply_rules --to content_generation` |
| M-30 学习报告 | `python -m src.tasks.learning.generate_report --period weekly` |

### 7.12 数据验证

| 用途 | 命令 |
|------|------|
| 验证素材 JSON | `python scripts/validate_material_json.py --type image --limit 5` |
| 验证内容 JSON | `python scripts/validate_content_json.py --stage copy --content-id CTN-2026-000001` |
| 验证合规 JSON | `python scripts/validate_compliance_json.py --content-id CTN-2026-000001` |
| 验证审阅 JSON | `python scripts/validate_review_json.py --task-id REV-2026-000001` |
| 验证发布 JSON | `python scripts/validate_publish_json.py --task-id PUB-2026-000001` |
| 验证效果 JSON | `python scripts/validate_performance_json.py --content-id CTN-2026-000001` |
| 验证规则 JSON | `python scripts/validate_rule_json.py --all` |
| 通用 JSON Schema 验证 | `python scripts/validate_json.py --schema <name> --file <path>` |
| 状态流转验证 | `python scripts/validate_status_transition.py --content-id CTN-2026-000001 --expected-status published` |

### 7.13 API 与任务调度

| 用途 | 命令 |
|------|------|
| 启动开发服务器 | `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` |
| 健康检查 | `curl http://localhost:8000/health` |
| Swagger 文档 | 浏览器访问 `http://localhost:8000/docs` |
| 启动 Celery Worker | `celery -A src.tasks.celery_app worker --loglevel=info` |
| 启动 Celery Beat | `celery -A src.tasks.celery_app beat --loglevel=info` |
| Worker + Beat 一起 | `celery -A src.tasks.celery_app worker --beat --loglevel=info` |
| 手动触发任务 | `python scripts/trigger_task.py --task daily_data_collection` |
| 查看任务历史 | `python scripts/task_history.py --days 7` |

### 7.14 存储管理

| 用途 | 命令 |
|------|------|
| 查看磁盘占用 | `du -sh data/files/materials/* data/files/outputs/*` |
| 清理临时文件 | `python scripts/cleanup_temp.py` |
| 查看磁盘空间 | `df -h data/files/` |
| 计算选题文件大小 | `find data/files/ -name "T2026-001_*" -exec du -ch {} + \| tail -1` |
| 归档旧报告 | `find data/files/reports/ -type f -mtime +30 -exec tar -rvf archive.tar {} \;` |
| 最近修改文件 | `find data/files/ -type f -mtime -7 \| sort` |

---

> **使用须知**：本文档为 Hermes 系统调试的唯一权威指南。所有模块开发、集成测试和故障排查必须严格遵循本文档定义的调试顺序和验收标准。调试过程中如发现本文档未覆盖的问题，请及时补充到对应章节。
>
> **最后更新**：2026-07-12
> **版本**：v1.0
