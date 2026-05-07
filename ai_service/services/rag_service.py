import json
import sqlite3
from pathlib import Path

from config import settings
from .embedding_service import EmbeddingService


class RAGService:
    def __init__(self, embedding_provider: EmbeddingService | None = None) -> None:
        self.embedding = embedding_provider or EmbeddingService()
        self.store_path = Path(settings.vector_store_path)
        self.documents = self._load_documents()

    def _load_documents(self) -> list[dict]:
        db_docs = self._load_documents_from_db()
        if db_docs:
            return db_docs

        if not self.store_path.exists():
            return []
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, list) else []
        except Exception:
            return []

    def _load_documents_from_db(self) -> list[dict]:
        url = (settings.database_url or "").strip()
        if not url.startswith("sqlite:///"):
            return []
        db_path = url.replace("sqlite:///", "", 1)
        db_file = (Path(__file__).resolve().parent.parent / db_path).resolve() if not Path(db_path).is_absolute() else Path(db_path)
        if not db_file.exists():
            return []

        docs: list[dict] = []
        try:
            conn = sqlite3.connect(str(db_file))
            cur = conn.cursor()
            # FAQs
            cur.execute("SELECT question, answer, category, language FROM faqs_faq WHERE is_active=1")
            for q, a, cat, lang in cur.fetchall():
                text = f"FAQ: {q} | {a}"
                docs.append({"text": text, "meta": {"type": "faq", "category": cat or "", "language": lang or ""}})
            # Products
            cur.execute("SELECT name, description, price, currency, return_policy, delivery_info FROM products_product WHERE is_active=1")
            for n, d, p, c, rp, di in cur.fetchall():
                text = f"Product: {n}. {d or ''} Price: {p} {c or 'BDT'}. Return: {rp or ''}. Delivery: {di or ''}"
                docs.append({"text": text, "meta": {"type": "product"}})
            conn.close()
        except Exception:
            return []
        return docs

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
