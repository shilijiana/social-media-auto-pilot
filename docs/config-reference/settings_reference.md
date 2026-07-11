# settings.yaml 配置项参考

> 本文档详细说明 `config/settings.yaml` 中每一个配置字段的含义、取值范围和使用场景。
> 目标受众: Hermes Agent, 开发人员, 运维人员

---

## 配置文件位置

```
config/settings.yaml
```

---

## 完整配置结构

```yaml
app:
  name: "Social Media Auto-Pilot"
  version: "0.1.0"
  debug: true

server:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  reload: true

database:
  url: "sqlite:///data/db/social_auto_pilot.db"
  echo: false
  pool_size: 5

storage:
  base_path: "data/files"
  temp_path: "data/files/temp"
  max_upload_size_mb: 500

llm:
  base_url: "${LLM_BASE_URL}"
  model: "${LLM_MODEL}"
  small_model: "${LLM_SMALL_MODEL}"
  max_tokens: 4096
  temperature: 0.7
  request_timeout: 60

browser:
  headless: true
  timeout: 30000
  max_concurrent: 1
  stealth_mode: true

media:
  ffmpeg_path: "ffmpeg"
  image_quality: 85
  video_bitrate: "2M"

scheduler:
  timezone: "Asia/Shanghai"

logging:
  level: "INFO"
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
  rotation: "10 MB"
  retention: "30 days"
```

---

## 1. app — 应用基本配置

### `app.name`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"Social Media Auto-Pilot"` |
| **说明** | 应用名称，用于日志标识、API 文档标题等 |

### `app.version`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"0.1.0"` |
| **说明** | 应用版本号，遵循语义化版本规范 |
| **影响范围** | API 响应头 `X-App-Version`、健康检查端点 |

### `app.debug`

| 属性 | 说明 |
|------|------|
| **类型** | boolean |
| **必填** | 是 |
| **默认值** | `true` |
| **说明** | 是否启用调试模式。开启后：详细错误信息、自动重载、SQL 日志（如 echo 开启） |
| **生产环境** | 必须设为 `false` |

---

## 2. server — 服务器配置

### `server.host`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"0.0.0.0"` |
| **说明** | FastAPI 服务监听地址。`0.0.0.0` 表示监听所有网络接口 |
| **安全注意** | 生产环境如仅内网访问，可改为 `127.0.0.1`，通过 Nginx 反向代理 |

### `server.port`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `8000` |
| **说明** | FastAPI 服务监听端口 |
| **冲突处理** | 如端口被占用，启动时会报错，需更换端口或释放占用 |

### `server.workers`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `1` |
| **说明** | Uvicorn worker 进程数。开发环境建议 1（配合 reload），生产环境建议 `CPU 核心数 × 2` |
| **注意** | 使用 SQLite 时，多 worker 可能导致数据库锁定问题 |

### `server.reload`

| 属性 | 说明 |
|------|------|
| **类型** | boolean |
| **必填** | 是 |
| **默认值** | `true` |
| **说明** | 是否启用热重载。代码变更时自动重启服务 |
| **生产环境** | 必须设为 `false` |

---

## 3. database — 数据库配置

### `database.url`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"sqlite:///data/db/social_auto_pilot.db"` |
| **说明** | 数据库连接字符串。支持 SQLite 和 PostgreSQL |
| **环境变量覆盖** | `DATABASE_URL` |
| **示例** | SQLite: `sqlite:///data/db/social_auto_pilot.db` |
|  | PostgreSQL: `postgresql://user:pass@host:5432/hermes` |

### `database.echo`

| 属性 | 说明 |
|------|------|
| **类型** | boolean |
| **必填** | 是 |
| **默认值** | `false` |
| **说明** | 是否在日志中输出 SQL 语句。调试时开启，生产环境关闭 |
| **环境变量覆盖** | `DB_ECHO` |

### `database.pool_size`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `5` |
| **说明** | 数据库连接池大小。SQLite 不支持连接池，仅 PostgreSQL 有效 |
| **推荐值** | 开发: 5, 生产: 20-50（取决于并发量） |

### `database.pool_recycle`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 否 |
| **默认值** | `3600` |
| **说明** | 连接回收时间（秒）。超过此时间的连接将被回收重建 |

---

## 4. storage — 文件存储配置

### `storage.base_path`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"data/files"` |
| **说明** | 文件存储根目录。所有素材、封面、视频文件存储在此目录下 |
| **子目录结构** | `materials/`、`covers/`、`videos/`、`exports/` |

### `storage.temp_path`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"data/files/temp"` |
| **说明** | 临时文件目录。处理中的文件暂存于此，完成后移动到正式目录 |
| **清理策略** | 定时任务清理超过 24 小时的临时文件 |

### `storage.max_upload_size_mb`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `500` |
| **说明** | 单次上传最大文件大小（MB）。超出此大小的上传将被拒绝 |
| **平台限制** | 抖音视频上限约 4GB，但建议限制在 500MB 以内 |

---

## 5. llm — 大语言模型配置

### `llm.base_url`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"${LLM_BASE_URL}"` |
| **说明** | LLM API 的基础 URL，兼容 OpenAI API 格式 |
| **环境变量** | 通过 `LLM_BASE_URL` 环境变量注入 |
| **示例** | `https://api.openai.com/v1` |

### `llm.model`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"${LLM_MODEL}"` |
| **说明** | 主模型名称，用于文案生成、评论分析等核心任务 |
| **环境变量** | 通过 `LLM_MODEL` 环境变量注入 |
| **示例** | `gpt-4o`, `claude-3-opus` |

### `llm.small_model`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"${LLM_SMALL_MODEL}"` |
| **说明** | 小模型名称，用于关键词扩展、标签生成等轻量任务 |
| **环境变量** | 通过 `LLM_SMALL_MODEL` 环境变量注入 |
| **示例** | `gpt-4o-mini`, `claude-3-haiku` |

### `llm.max_tokens`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `4096` |
| **说明** | 单次 LLM 请求的最大输出 token 数 |
| **调整建议** | 文案生成建议 2048-4096，评论分析建议 1024 |

### `llm.temperature`

| 属性 | 说明 |
|------|------|
| **类型** | number |
| **必填** | 是 |
| **默认值** | `0.7` |
| **说明** | LLM 生成温度（0-2）。越高越有创意，越低越稳定 |
| **推荐值** | 文案生成: 0.7-0.9, 分析任务: 0.1-0.3 |

### `llm.request_timeout`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `60` |
| **说明** | LLM API 请求超时时间（秒）。超时后将抛出异常并重试 |

---

## 6. browser — 浏览器自动化配置

### `browser.headless`

| 属性 | 说明 |
|------|------|
| **类型** | boolean |
| **必填** | 是 |
| **默认值** | `true` |
| **说明** | Playwright 是否使用无头模式。`true` = 无界面运行 |
| **调试** | 设为 `false` 可看到浏览器操作过程 |

### `browser.timeout`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `30000` |
| **说明** | 浏览器操作超时时间（毫秒）。包括页面加载、元素等待等 |
| **调整建议** | 网络较差时可适当增大 |

### `browser.max_concurrent`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `1` |
| **说明** | 最大并发浏览器实例数。限制同时打开的浏览器窗口数量 |
| **资源考虑** | 每个浏览器实例消耗约 500MB-1GB 内存 |

### `browser.stealth_mode`

| 属性 | 说明 |
|------|------|
| **类型** | boolean |
| **必填** | 是 |
| **默认值** | `true` |
| **说明** | 是否启用反检测模式。模拟真实用户行为，避免被平台识别为爬虫 |
| **重要** | 强烈建议保持开启，关闭后可能被平台封禁 |

---

## 7. media — 媒体处理配置

### `media.ffmpeg_path`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"ffmpeg"` |
| **说明** | FFmpeg 可执行文件路径。默认使用系统 PATH 中的 ffmpeg |
| **Docker** | 容器中已预装，无需修改 |

### `media.image_quality`

| 属性 | 说明 |
|------|------|
| **类型** | integer |
| **必填** | 是 |
| **默认值** | `85` |
| **说明** | 图片输出质量（1-100）。影响封面图、素材缩略图的压缩质量 |
| **推荐值** | 封面图: 90-95, 缩略图: 70-80 |

### `media.video_bitrate`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"2M"` |
| **说明** | 视频输出码率。格式为 `数字+单位`（K/M） |
| **推荐值** | 短视频: 1M-2M, 高清长视频: 4M-8M |

---

## 8. scheduler — 任务调度配置

### `scheduler.timezone`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"Asia/Shanghai"` |
| **说明** | 定时任务时区。所有定时任务（数据采集、报告生成等）基于此时区 |
| **注意** | Celery Beat 和系统 cron 均需使用此时区 |

---

## 9. logging — 日志配置

### `logging.level`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"INFO"` |
| **说明** | 日志输出级别 |
| **可选值** | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| **推荐** | 开发: `DEBUG`, 生产: `INFO` |

### `logging.format`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"{time:YYYY-MM-DD HH:mm:ss} \| {level} \| {name}:{function}:{line} \| {message}"` |
| **说明** | Loguru 日志输出格式 |
| **变量** | `{time}`, `{level}`, `{name}`, `{function}`, `{line}`, `{message}` |

### `logging.rotation`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"10 MB"` |
| **说明** | 日志文件轮转策略。当日志文件达到指定大小时自动轮转 |
| **其他格式** | `"1 day"`, `"1 week"`, `"00:00"` (每天零点) |

### `logging.retention`

| 属性 | 说明 |
|------|------|
| **类型** | string |
| **必填** | 是 |
| **默认值** | `"30 days"` |
| **说明** | 日志文件保留时间。超过此时间的旧日志将被自动删除 |
| **其他格式** | `"7 days"`, `"1 week"`, `"3 months"` |

---

## 10. 环境变量覆盖

以下配置项支持通过环境变量覆盖，环境变量优先级高于 YAML 文件：

| 配置项 | 环境变量 | 说明 |
|--------|---------|------|
| `database.url` | `DATABASE_URL` | 数据库连接串 |
| `database.echo` | `DB_ECHO` | SQL 日志开关 |
| `llm.base_url` | `LLM_BASE_URL` | LLM API 地址 |
| `llm.model` | `LLM_MODEL` | 主模型名称 |
| `llm.small_model` | `LLM_SMALL_MODEL` | 小模型名称 |
| `server.port` | `PORT` | 服务端口 |
| `logging.level` | `LOG_LEVEL` | 日志级别 |

### 使用示例

```bash
# 通过环境变量覆盖配置
export DATABASE_URL="postgresql://user:pass@localhost:5432/hermes"
export LLM_MODEL="gpt-4o"
export LOG_LEVEL="DEBUG"

# 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 11. 配置验证规则

启动时系统会自动验证以下配置项：

| 验证项 | 规则 | 失败处理 |
|--------|------|---------|
| `server.port` | 1-65535 之间 | 启动失败 |
| `database.url` | 有效连接串格式 | 启动失败 |
| `llm.base_url` | 有效 URL 格式 | 警告，LLM 功能不可用 |
| `llm.model` | 非空字符串 | 警告，LLM 功能不可用 |
| `storage.base_path` | 目录可写 | 启动失败 |
| `media.ffmpeg_path` | 可执行文件存在 | 警告，视频处理功能不可用 |

---

> **版本**: v1.0 | **最后更新**: 2026-07-12 | **对应文件**: `config/settings.yaml`
