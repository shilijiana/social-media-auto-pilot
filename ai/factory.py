"""AI Provider 工厂 — 根据配置动态创建 Provider 实例。"""

from autosoc.ai.interfaces import AbstractAIProvider
from autosoc.core.config import settings
from autosoc.core.logging import log


def create_ai_provider() -> AbstractAIProvider:
    """根据 settings.ai_provider 创建相应 Provider 实例。

    当前支持:
    - mock: MockAIProvider（开发/测试用）
    - openai: OpenAIProvider（需安装 openai 包并配置 API Key）
    - ollama: OllamaProvider（需运行本地 Ollama 服务）
    """
    provider_name = settings.ai_provider

    if provider_name == "mock":
        from autosoc.ai.providers.mock_provider import MockAIProvider

        log.info("[AI] 使用 Mock Provider（开发模式）")
        return MockAIProvider()

    elif provider_name == "openai":
        try:
            from autosoc.ai.providers.openai_provider import OpenAIProvider
        except ImportError:
            raise ImportError(
                "OpenAI Provider 需要安装 openai 包: pip install autosoc[ai]"
            )

        log.info(f"[AI] 使用 OpenAI Provider (model={settings.openai_model})")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    elif provider_name == "ollama":
        from autosoc.ai.providers.ollama_provider import OllamaProvider

        log.info(f"[AI] 使用 Ollama Provider (url={settings.ollama_base_url})")
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )

    else:
        raise ValueError(f"不支持的 AI Provider: {provider_name}，可选: mock, openai, ollama")
