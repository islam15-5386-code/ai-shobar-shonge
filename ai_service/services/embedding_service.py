import hashlib
import math
import re

from config import settings


class EmbeddingService:
    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self.model = settings.embedding_model

    @staticmethod
    def _tokens(text: str) -> list[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower().strip())
        return [token for token in cleaned.split() if token]

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in self._tokens(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = -1.0 if ((h >> 8) & 1) else 1.0
            vec[idx] += sign

        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
