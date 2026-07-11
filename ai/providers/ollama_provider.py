"""
Ollama Provider 实现 — 通过 Ollama 本地 API 调用本地模型。

使用前需安装 ollama 并运行: ollama serve
"""

from typing import Dict, List

import requests

from autosoc.ai.interfaces import (
    AbstractAIProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    TextGenerationRequest,
    TextGenerationResponse,
)


class OllamaProvider(AbstractAIProvider):
    """Ollama Provider — 调用本地部署的开源模型。"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _chat(self, messages: list, options: dict = None) -> dict:
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "options": options or {},
                "stream": False,
            },
        )
        resp.raise_for_status()
        return resp.json()

    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        result = self._chat(messages, {"temperature": request.temperature})

        return TextGenerationResponse(
            text=result.get("message", {}).get("content", ""),
            model_used=self.model,
            tokens_used=result.get("eval_count", 0),
        )

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        raise NotImplementedError("Ollama 当前不支持图像生成")

    def analyze_sentiment(self, text: str) -> Dict:
        messages = [
            {
                "role": "system",
                "content": "分析以下文本的情感。仅返回JSON: "
                           '{"sentiment": "positive|neutral|negative", "score": 0.0-1.0}',
            },
            {"role": "user", "content": text},
        ]
        result = self._chat(messages)
        import json
        content = result.get("message", {}).get("content", '{"sentiment":"neutral","score":0.5}')
        return json.loads(content)

    def embed_text(self, request: EmbeddingRequest) -> EmbeddingResponse:
        embeddings = []
        for text in request.texts:
            resp = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": request.model, "prompt": text},
            )
            resp.raise_for_status()
            embeddings.append(resp.json().get("embedding", []))

        return EmbeddingResponse(embeddings=embeddings, model_used=request.model)

    def generate_keywords(self, seed_words: List[str], count: int = 10) -> List[str]:
        prompt = (
            f"基于以下种子词，生成 {count} 个相关的扩展关键词、同义词和长尾词，"
            f"以逗号分隔返回：{', '.join(seed_words)}"
        )
        resp = self.generate_text(TextGenerationRequest(prompt=prompt, max_tokens=200))
        return [kw.strip() for kw in resp.text.split(",") if kw.strip()]
