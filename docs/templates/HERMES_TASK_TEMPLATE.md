# Hermes Agent 任务描述模板

> **用途**：此模板用于向 Hermes agent 提交单模块调试任务。使用者将 `{{占位符}}` 替换为实际值后发送给 Hermes。
> **适用场景**：P0/P1/P2 各阶段模块的单元调试与集成联调。
> **最后更新**：2026-07-12

---

## 使用说明

1. 复制下方"任务模板"部分
2. 将所有 `{{占位符}}` 替换为实际值
3. 将替换后的完整内容发送给 Hermes agent
4. Hermes 将按照"执行步骤"依次完成调试工作

---

## 任务模板

---

# 任务: 调试 {{MODULE_ID}} {{MODULE_NAME}}

## 模块信息
- **模块编号**: {{MODULE_ID}}
- **模块名称**: {{MODULE_NAME}}
- **所属大类**: {{CATEGORY}}
- **优先级**: {{PRIORITY}}
- **源代码路径**: `src/services/{{PACKAGE}}/{{MODULE_FILE}}.py`
- **文档路径**: `docs/modules/{{MODULE_ID}}_{{MODULE_NAME}}.md`

## 前置条件
1. 确认以下上游模块已完成调试:
   {{UPSTREAM_MODULES}}
2. 确认基础设施已就绪:
   - [ ] 数据库: `python scripts/init_db.py` 执行成功
   - [ ] LLM: API Key 已配置且可调用
   - [ ] 存储: `data/files/` 目录可读写
   {{INFRA_DEPS}}

## 执行步骤
1. **读取文档**: 完整阅读 `docs/modules/{{MODULE_ID}}_{{MODULE_NAME}}.md`
2. **检查配置**: 确认 `config/settings.yaml` 中相关配置项正确
3. **准备测试数据**: 
   - 输入数据来源: {{INPUT_SOURCE}}
   - 测试数据位置: {{TEST_DATA_PATH}}
4. **运行模块**:
   ```bash
   python -m src.services.{{PACKAGE}}.{{MODULE_FILE}} --dry-run
   ```
5. **验证输出**:
   - 检查输出 JSON 格式是否匹配 Schema（参考 `docs/INTERFACE_CONTRACT.md`）
   - 检查数据库写入是否正确（表: {{DB_TABLES}}）
   - 检查文件输出路径是否正确（路径: {{OUTPUT_PATHS}}）
6. **验证错误处理**:
   - 模拟 {{ERROR_SCENARIO}} 场景
   - 确认降级策略生效

## 验收标准
- [ ] 输入校验通过，格式不正确的输入被正确拒绝
- [ ] 核心处理逻辑无异常，所有 Step 执行完成
- [ ] 输出 JSON 格式与 `docs/INTERFACE_CONTRACT.md` 中定义的 Schema 一致
- [ ] 数据库记录写入正确（表: {{DB_TABLES}}）
- [ ] 文件输出到正确路径（路径: {{OUTPUT_PATHS}}）
- [ ] 错误场景有正确的降级处理
- [ ] 日志输出完整，包含关键步骤的执行记录
- [ ] 自学习数据已生成（如适用）

## 注意事项
{{NOTES}}

## 相关文档
- 模块说明: `docs/modules/{{MODULE_ID}}_{{MODULE_NAME}}.md`
- 接口契约: `docs/INTERFACE_CONTRACT.md`
- 基础设施: `docs/INFRASTRUCTURE.md`
- 调试大纲: `docs/DEBUGGING_GUIDE.md`
- 数据流转: `docs/data-flow/{{FLOW_DOC}}.md`

---

## 填写示例: M-08 文案差异化生成

> 以下是将上述模板中所有占位符替换为 M-08 实际值后的完整任务描述，供参考。

---

# 任务: 调试 M-08 文案差异化生成

## 模块信息
- **模块编号**: M-08
- **模块名称**: 文案差异化生成
- **所属大类**: 内容生产
- **优先级**: P0
- **源代码路径**: `src/services/content/generate_copy.py`
- **文档路径**: `docs/modules/M-08_文案差异化生成.md`

## 前置条件
1. 确认以下上游模块已完成调试:
   - M-02 图文素材采集（素材库中有可用于测试的图文素材）
   - M-03 视频素材采集（素材库中有可用于测试的视频素材）
   - M-07 素材匹配与调用（能根据选题 ID 返回匹配的素材列表）
2. 确认基础设施已就绪:
   - [x] 数据库: `python scripts/init_db.py` 执行成功
   - [x] LLM: API Key 已配置且可调用
   - [x] 存储: `data/files/` 目录可读写
   - [x] LLM Prompt 模板: `src/infrastructure/llm/prompts/content/copywriting.j2` 语法正确

## 执行步骤
1. **读取文档**: 完整阅读 `docs/modules/M-08_文案差异化生成.md`
2. **检查配置**: 确认 `config/settings.yaml` 中 `llm` 节点配置正确（model、temperature、max_tokens 等）
3. **准备测试数据**: 
   - 输入数据来源: M-07 素材匹配与调用的输出结果（Content partial JSON，含 topic_id、platform、material_refs、tags）
   - 测试数据位置: 通过 `python scripts/create_test_topic.py --topic "AI技术趋势" --platform douyin --keywords "AI,人工智能,大模型"` 创建测试选题 T2026-001，再运行 M-07 获取匹配素材
4. **运行模块**:
   ```bash
   # 为抖音生成文案
   python -m src.tasks.content.generate_copy \
     --topic-id T2026-001 \
     --platform douyin \
     --style professional \
     --output data/files/outputs/copywriting/

   # 为小红书生成文案（验证多平台差异化）
   python -m src.tasks.content.generate_copy \
     --topic-id T2026-001 \
     --platform xiaohongshu \
     --style friendly

   # 为B站生成文案
   python -m src.tasks.content.generate_copy \
     --topic-id T2026-001 \
     --platform bilibili \
     --style technical
   ```
5. **验证输出**:
   - 检查输出 JSON 格式是否匹配 Schema（参考 `docs/INTERFACE_CONTRACT.md` 中 4.2.1 Content 对象定义）
   - 检查数据库写入是否正确（表: `content_drafts`）
   - 检查文件输出路径是否正确（路径: `data/files/outputs/copywriting/`）
6. **验证错误处理**:
   - 模拟 LLM 调用超时场景（设置 timeout=1 或使用无效 API Key）
   - 确认降级策略生效（自动切换到 `LLM_SMALL_MODEL`，重试最多 3 次）

## 验收标准
- [ ] 输入校验通过，topic_id 格式不正确（非 TYYYY-NNN 格式）的输入被正确拒绝
- [ ] 核心处理逻辑无异常，LLM 调用、JSON 解析、数据库写入全部执行完成
- [ ] 输出 JSON 格式与 `docs/INTERFACE_CONTRACT.md` 中 4.2.1 Content Schema 一致（包含 content_id、topic_id、platform、copytext、tags 等必填字段）
- [ ] 数据库记录写入正确（表: `content_drafts`）
- [ ] 文件输出到正确路径（路径: `data/files/outputs/copywriting/`，文件名符合 `[选题编号]_M08_[平台]_v[版本]_[日期].json` 规范）
- [ ] 错误场景有正确的降级处理（LLM 超时时自动重试，主模型不可用时切换轻量模型）
- [ ] 日志输出完整，包含关键步骤的执行记录（LLM 调用耗时、token 消耗、生成结果摘要）
- [ ] 多平台文案存在明显差异化（不同平台的文案在风格、长度、标签上各有不同，非简单复制）
- [ ] 文案字数符合平台限制（抖音 ≤ 1000 字，小红书 ≤ 1000 字，B站无硬性限制，X ≤ 280 字符）

## 注意事项
- 本模块强依赖 LLM，调试前务必确认 `LLM_API_KEY` 和 `LLM_MODEL` 配置正确
- 首次运行建议使用 `--dry-run` 参数验证流程，确认无误后再正式执行
- 多平台差异化是核心验收点，不要用同一段文案改改标签就发给不同平台
- 生成的 content_id 必须符合 `CTN-YYYY-NNNNNN` 格式，确保全局唯一
- 如果 LLM 返回的 JSON 解析失败，检查 `logs/llm_calls.log` 中的原始响应内容

## 相关文档
- 模块说明: `docs/modules/M-08_文案差异化生成.md`
- 接口契约: `docs/INTERFACE_CONTRACT.md`（4.2.1 Content 对象定义）
- 基础设施: `docs/INFRASTRUCTURE.md`（3. LLM 调用 章节）
- 调试大纲: `docs/DEBUGGING_GUIDE.md`（2.1.3 步骤 4: M-08 文案差异化生成）
- 数据流转: `docs/data-flow/content-production-flow.md`
