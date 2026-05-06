from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import UploadFile

from config import settings
from .embedding_service import EmbeddingService
from .llm_service import GeminiLLMService, LLMService
from .whisper_service import WhisperService


class LLMProvider(Protocol):
    def generate_reply(self, message: str, context: list[str], locale: str = "en") -> str: ...

    @property
    def model_name(self) -> str: ...


class EmbeddingProvider(Protocol):
    model: str

    def embed(self, text: str) -> list[float]: ...

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float: ...


class WhisperProvider(Protocol):
    async def transcribe(self, file: UploadFile) -> str: ...


class LocalCPUEmbeddingProvider(EmbeddingService):
    pass


class LocalCPULLMProvider(LLMService):
    pass


class LocalCPUWhisperProvider(WhisperService):
    pass


class LocalGPUEmbeddingProvider(EmbeddingService):
    def __init__(self, dim: int = 64) -> None:
        super().__init__(dim=dim)
        self.model = settings.local_embedding_model


class LocalGPULLMProvider(LLMService):
    @property
    def model_name(self) -> str:
        return settings.local_llm_model


class LocalGPUWhisperProvider(WhisperService):
    pass


class GeminiLLMProvider(GeminiLLMService):
    pass


@dataclass(frozen=True)
class ProviderBundle:
    llm: LLMProvider
    embedding: EmbeddingProvider
    whisper: WhisperProvider
    mode: str


def create_provider_bundle() -> ProviderBundle:
    mode = settings.ai_mode
    llm_provider = settings.llm_provider
    embedding_provider = settings.embedding_provider
    whisper_provider = settings.whisper_provider

    if mode == "gpu" and llm_provider == "local" and embedding_provider == "local" and whisper_provider == "local":
        return ProviderBundle(
            llm=LocalGPULLMProvider(),
            embedding=LocalGPUEmbeddingProvider(),
            whisper=LocalGPUWhisperProvider(),
            mode=mode,
        )

    return ProviderBundle(
        llm=LocalCPULLMProvider(),
        embedding=LocalCPUEmbeddingProvider(),
        whisper=LocalCPUWhisperProvider(),
        mode="cpu",
    )
    if llm_provider == "gemini":
        return ProviderBundle(
            llm=GeminiLLMProvider(),
            embedding=LocalCPUEmbeddingProvider() if embedding_provider == "local" else LocalCPUEmbeddingProvider(),
            whisper=LocalCPUWhisperProvider() if whisper_provider == "local" else LocalCPUWhisperProvider(),
            mode=mode if mode in {"cpu", "gpu"} else "cpu",
        )
