"""Mock AI Provider — 开发/测试时返回预设响应，不依赖外部 API。"""

from typing import Dict, List

from autosoc.ai.interfaces import (
    AbstractAIProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    TextGenerationRequest,
    TextGenerationResponse,
)

_MOCK_TEXT = """这是一个 AI 生成的示范文案。

🔥 你绝对想不到的 [TOPIC] 秘密！

1. 第一点：这是我们实测发现的
2. 第二点：99%的人都不知道
3. 第三点：看完你会回来感谢我

#热门标签 #实用技巧 #干货分享

👉 关注我，获取更多干货！"""

_MOCK_IMAGE = b"mock_image_data_png_placeholder"


class MockAIProvider(AbstractAIProvider):
    """开发/测试用的 Mock Provider，返回固定预设内容。"""

    def __init__(self, model: str = "mock-model"):
        self.model = model

    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        return TextGenerationResponse(
            text=_MOCK_TEXT.replace("[TOPIC]", request.prompt[:30]),
            model_used=self.model,
            tokens_used=150,
        )

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        return ImageGenerationResponse(
            image_data=_MOCK_IMAGE,
            format="png",
            model_used=f"{self.model}-image",
        )

    def analyze_sentiment(self, text: str) -> Dict:
        return {"sentiment": "positive", "score": 0.85}

    def embed_text(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(
            embeddings=[[0.1] * 128 for _ in request.texts],
            model_used=self.model,
            tokens_used=len(request.texts) * 10,
        )

    def generate_keywords(self, seed_words: List[str], count: int = 10) -> List[str]:
        return [f"{w}_扩展词_{i}" for w in seed_words for i in range(3)]
