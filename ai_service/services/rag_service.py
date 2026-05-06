import json
from pathlib import Path

from config import settings
from services.embedding_service import EmbeddingService


class RAGService:
    def __init__(self) -> None:
        self.embedding = EmbeddingService()
        self.store_path = Path(settings.vector_store_path)
        self.documents = self._load_documents()

    def _load_documents(self) -> list[dict]:
        if not self.store_path.exists():
            return []
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, list) else []
        except Exception:
            return []

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        if not self.documents:
            return []

        qv = self.embedding.embed(query)
        scored: list[tuple[float, dict]] = []
        for doc in self.documents:
            text = str(doc.get("text", "")).strip()
            if not text:
                continue
            dv = doc.get("vector") or self.embedding.embed(text)
            sim = self.embedding.cosine_similarity(qv, dv)
            scored.append((sim, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        k = top_k or settings.top_k
        return [{"score": s, **d} for s, d in scored[:k]]
