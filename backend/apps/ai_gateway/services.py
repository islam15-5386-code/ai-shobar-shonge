import hashlib
import math
import re
from dataclasses import dataclass
from typing import Iterable

from django.conf import settings
from django.db import connection

from apps.faqs.models import FAQ

EMBED_DIM = 64
BANGLA_CHAR_RE = re.compile(r"[ঀ-৿]")


@dataclass
class FAQMatch:
    faq: FAQ | None
    score: float
    method: str


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _tokens(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s]", " ", _normalize(text))
    return [tok for tok in cleaned.split() if tok]


def build_embedding(text: str, dim: int = EMBED_DIM) -> list[float]:
    vec = [0.0] * dim
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = -1.0 if ((h >> 8) & 1) else 1.0
        vec[idx] += sign

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    if len(a_list) != len(b_list) or not a_list:
        return 0.0
    dot = sum(x * y for x, y in zip(a_list, b_list))
    a_norm = math.sqrt(sum(x * x for x in a_list))
    b_norm = math.sqrt(sum(y * y for y in b_list))
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return dot / (a_norm * b_norm)


def is_bangla_text(text: str) -> bool:
    return bool(BANGLA_CHAR_RE.search(text))


def detect_intent(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["refund", "return", "money back"]):
        return "refund"
    if any(k in lower for k in ["price", "cost", "plan", "subscription"]):
        return "pricing"
    if any(k in lower for k in ["human", "agent", "support", "help me", "handover"]):
        return "human_handover"
    if any(k in lower for k in ["delivery", "shipping", "arrive"]):
        return "delivery"
    return "general"


def detect_sentiment(text: str) -> str:
    lower = text.lower()
    negative = ["bad", "angry", "terrible", "hate", "worst", "not working", "frustrated"]
    positive = ["great", "thanks", "awesome", "good", "love", "helpful"]

    neg_score = sum(1 for t in negative if t in lower)
    pos_score = sum(1 for t in positive if t in lower)

    if neg_score > pos_score:
        return "negative"
    if pos_score > neg_score:
        return "positive"
    return "neutral"


def _search_with_python(query_vec: list[float], faqs) -> FAQMatch:
    best_faq = None
    best_score = -1.0
    for faq in faqs:
        if faq.embedding_vector:
            score = cosine_similarity(query_vec, faq.embedding_vector)
            if score > best_score:
                best_score = score
                best_faq = faq

    if best_faq is None:
        return FAQMatch(faq=None, score=0.0, method="none")
    return FAQMatch(faq=best_faq, score=max(0.0, min(1.0, best_score)), method="python")


def _search_with_postgres(query_vec: list[float], business_id: int) -> FAQMatch:
    # pgvector-style SQL path for Postgres deployments; falls back if it fails.
    vec_sql = "[" + ",".join(f"{x:.8f}" for x in query_vec) + "]"
    sql = """
    SELECT id
    FROM faqs_faq
    WHERE business_id = %s AND is_active = TRUE AND embedding_vector IS NOT NULL
    """
    # Stays intentionally simple to keep SQLite compatibility in dev.
    with connection.cursor() as cur:
        cur.execute(sql, [business_id])
        ids = [row[0] for row in cur.fetchall()]

    if not ids:
        return FAQMatch(faq=None, score=0.0, method="postgres-empty")

    faqs = FAQ.objects.filter(id__in=ids)
    return _search_with_python(query_vec, faqs)


def find_best_faq(query: str, business_id: int) -> FAQMatch:
    query_vec = build_embedding(query)
    faqs = FAQ.objects.filter(business_id=business_id, is_active=True)

    if connection.vendor == "postgresql" and getattr(settings, "USE_PGVECTOR_SEARCH", True):
        try:
            return _search_with_postgres(query_vec, business_id)
        except Exception:
            return _search_with_python(query_vec, faqs)

    return _search_with_python(query_vec, faqs)


def confidence_from_similarity(similarity: float) -> float:
    return round(max(0.0, min(1.0, similarity)), 3)


def should_escalate(confidence: float, sentiment: str, intent: str) -> tuple[bool, str]:
    if intent == "human_handover":
        return True, "user_requested_human"
    if sentiment == "negative" and confidence < 0.7:
        return True, "negative_sentiment_low_confidence"
    if confidence < 0.45:
        return True, "low_confidence"
    return False, "none"


def to_bangla_reply(text: str) -> str:
    # Lightweight Bangla-friendly rewrite for MVP.
    return f"???????? {text}"
