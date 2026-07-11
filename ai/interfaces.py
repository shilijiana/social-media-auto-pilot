"""AI 服务抽象层 — 定义所有 AI 能力的接口和数据模型。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── 数据模型 ──────────────────────────────────────────

@dataclass
class TextGenerationRequest:
    prompt: str
    max_tokens: int = 2000
    temperature: float = 0.7
    system_prompt: str = ""
    stop_sequences: List[str] = field(default_factory=list)


@dataclass
class TextGenerationResponse:
    text: str
    model_used: str
    tokens_used: int = 0
    finish_reason: str = "stop"


@dataclass
class ImageGenerationRequest:
    prompt: str
    size: tuple = (1080, 1920)
    style: str = "realistic"
    negative_prompt: str = ""


@dataclass
class ImageGenerationResponse:
    image_data: bytes
    format: str = "png"
    model_used: str = ""


@dataclass
class EmbeddingRequest:
    texts: List[str]
    model: str = "text-embedding-3-small"


@dataclass
class EmbeddingResponse:
    embeddings: List[List[float]]
    model_used: str = ""
    tokens_used: int = 0


# ── 抽象接口 ──────────────────────────────────────────

class AbstractAIProvider(ABC):
    """AI Provider 抽象基类 — 所有 AI 能力接口。

    实现类需覆盖所有 abstractmethod。
    通过 Factory 在启动时根据配置动态创建实例。
    """

    @abstractmethod
    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """文本生成（文案、标题、评论回复等）。"""
        ...

    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """图像生成（封面底图、配图等）。"""
        ...

    @abstractmethod
    def analyze_sentiment(self, text: str) -> Dict:
        """情感分析，返回 {'sentiment': 'positive|neutral|negative', 'score': 0.0-1.0}。"""
        ...

    @abstractmethod
    def embed_text(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """文本向量化，用于语义搜索 / 聚类 / 相似度匹配。"""
        ...

    @abstractmethod
    def generate_keywords(self, seed_words: List[str], count: int = 10) -> List[str]:
        """根据种子词生成扩展关键词列表。"""
        ...

    def transcribe_audio(self, audio_path: str) -> str:
        """语音转文字（可选，默认不支持）。"""
        raise NotImplementedError
