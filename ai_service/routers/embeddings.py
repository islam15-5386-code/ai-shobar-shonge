from fastapi import APIRouter

from models import EmbeddingItem, EmbeddingRequest, EmbeddingResponse
from services.runtime import providers

router = APIRouter()


@router.post("/", response_model=EmbeddingResponse)
def generate_embeddings(payload: EmbeddingRequest) -> EmbeddingResponse:
    items = [EmbeddingItem(text=t, vector=providers.embedding.embed(t)) for t in payload.texts]
    return EmbeddingResponse(model=providers.embedding.model, items=items)
