"""OpenAI Provider 实现 — 通过 OpenAI API 调用 AI 能力。"""

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


class OpenAIProvider(AbstractAIProvider):
    """OpenAI API Provider — 支持 GPT-4o、DALL-E 等模型。"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        client = self._get_client()
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=request.stop_sequences or None,
        )

        return TextGenerationResponse(
            text=resp.choices[0].message.content or "",
            model_used=self.model,
            tokens_used=resp.usage.total_tokens if resp.usage else 0,
            finish_reason=resp.choices[0].finish_reason or "stop",
        )

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        client = self._get_client()
        resp = client.images.generate(
            model="dall-e-3",
            prompt=request.prompt,
            size=f"{request.size[0]}x{request.size[1]}",
            quality="standard",
            n=1,
        )

        import requests as http_requests
        image_url = resp.data[0].url
        image_data = http_requests.get(image_url).content

        return ImageGenerationResponse(
            image_data=image_data,
            format="png",
            model_used="dall-e-3",
        )

    def analyze_sentiment(self, text: str) -> Dict:
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "分析以下文本的情感。仅返回JSON: "
                               '{"sentiment": "positive|neutral|negative", "score": 0.0-1.0}',
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )
        import json
        return json.loads(resp.choices[0].message.content or '{"sentiment":"neutral","score":0.5}')

    def embed_text(self, request: EmbeddingRequest) -> EmbeddingResponse:
        client = self._get_client()
        resp = client.embeddings.create(
            model=request.model,
            input=request.texts,
        )
        return EmbeddingResponse(
            embeddings=[d.embedding for d in resp.data],
            model_used=request.model,
            tokens_used=resp.usage.total_tokens if resp.usage else 0,
        )

    def generate_keywords(self, seed_words: List[str], count: int = 10) -> List[str]:
        prompt = (
            f"基于以下种子词，生成 {count} 个相关的扩展关键词、同义词和长尾词，"
            f"以逗号分隔返回：{', '.join(seed_words)}"
        )
        resp = self.generate_text(TextGenerationRequest(prompt=prompt, max_tokens=200))
        return [kw.strip() for kw in resp.text.split(",") if kw.strip()]
