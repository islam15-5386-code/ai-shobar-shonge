from fastapi import APIRouter

from models import EmbeddingItem, EmbeddingRequest, EmbeddingResponse
from services import EmbeddingService

router = APIRouter()
embedding_service = EmbeddingService()


@router.post("/", response_model=EmbeddingResponse)
def generate_embeddings(payload: EmbeddingRequest) -> EmbeddingResponse:
    items = [EmbeddingItem(text=t, vector=embedding_service.embed(t)) for t in payload.texts]
    return EmbeddingResponse(model=embedding_service.model, items=items)
