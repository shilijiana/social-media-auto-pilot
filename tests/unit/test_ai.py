"""AI 抽象层测试。"""

import pytest


class TestAIInterfaces:
    def test_mock_provider_text(self):
        from autosoc.ai.providers.mock_provider import MockAIProvider
        from autosoc.ai.interfaces import TextGenerationRequest

        provider = MockAIProvider()
        resp = provider.generate_text(
            TextGenerationRequest(prompt="写一篇关于AI的文章")
        )

        assert resp.text
        assert resp.model_used == "mock-model"
        assert resp.tokens_used > 0

    def test_mock_provider_image(self):
        from autosoc.ai.providers.mock_provider import MockAIProvider
        from autosoc.ai.interfaces import ImageGenerationRequest

        provider = MockAIProvider()
        resp = provider.generate_image(
            ImageGenerationRequest(prompt="一只猫")
        )

        assert resp.image_data
        assert resp.format == "png"

    def test_mock_provider_sentiment(self):
        from autosoc.ai.providers.mock_provider import MockAIProvider

        provider = MockAIProvider()
        result = provider.analyze_sentiment("这个产品非常好用！")

        assert "sentiment" in result
        assert result["sentiment"] == "positive"

    def test_mock_provider_keywords(self):
        from autosoc.ai.providers.mock_provider import MockAIProvider

        provider = MockAIProvider()
        keywords = provider.generate_keywords(["AI", "机器学习"], count=6)

        assert len(keywords) >= 6

    def test_factory_mock(self, monkeypatch):
        monkeypatch.setenv("AUTOSOC_AI_PROVIDER", "mock")
        from autosoc.core.config import Settings
        monkeypatch.setattr("autosoc.core.config.settings", Settings())

        from autosoc.ai.factory import create_ai_provider
        provider = create_ai_provider()

        from autosoc.ai.providers.mock_provider import MockAIProvider
        assert isinstance(provider, MockAIProvider)
