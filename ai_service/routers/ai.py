from fastapi import APIRouter, File, UploadFile

from models import (
    AIRespondRequest,
    AIRespondResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    IntentRequest,
    IntentResponse,
    ReindexRequest,
    ReindexResponse,
    SentimentRequest,
    SentimentResponse,
    VoiceResponse,
)
from services import IntentService, RAGService, SentimentService
from services.runtime import providers

router = APIRouter()

intent_service = IntentService()
sentiment_service = SentimentService()
rag_service = RAGService(embedding_provider=providers.embedding)


@router.get("/health")
def ai_health() -> dict:
    try:
        import torch  # type: ignore

        cuda_available = bool(torch.cuda.is_available())
    except Exception:
        cuda_available = False
    return {"status": "ok", "ai_mode": providers.mode, "cuda_available": cuda_available}


@router.post("/respond", response_model=AIRespondResponse)
def respond(payload: AIRespondRequest) -> AIRespondResponse:
    intent, intent_conf = intent_service.detect(payload.message)
    sentiment, sent_score = sentiment_service.analyze(payload.message)
    docs = rag_service.retrieve(payload.message)
    sources = [str(d.get("text", "")) for d in docs if d.get("text")]
    answer = providers.llm.generate_reply(payload.message, context=sources, locale=payload.locale)
    confidence = round((intent_conf + sent_score) / 2, 3)
    should_escalate = confidence < 0.6 or intent in ["refund", "human_handover"] or sentiment == "negative"

    if should_escalate and not sources:
        if payload.locale.lower().startswith("bn"):
            answer = "আমি নিশ্চিত উত্তর দিতে পারছি না। একজন মানব সাপোর্ট এজেন্ট শীঘ্রই সহায়তা করবে।"
        else:
            answer = "I am not fully confident about this answer. A human support agent will assist you shortly."

    return AIRespondResponse(
        answer=answer,
        confidence=confidence,
        intent=intent,
        sentiment=sentiment,
        should_escalate=should_escalate,
        sources=sources,
        model_name=getattr(providers.llm, "model_name", "mock"),
    )


@router.post("/intent", response_model=IntentResponse)
def intent(payload: IntentRequest) -> IntentResponse:
    name, conf = intent_service.detect(payload.text)
    return IntentResponse(intent=name, confidence=conf)


@router.post("/sentiment", response_model=SentimentResponse)
def sentiment(payload: SentimentRequest) -> SentimentResponse:
    name, score = sentiment_service.analyze(payload.text)
    return SentimentResponse(sentiment=name, score=score)


@router.post("/embed", response_model=EmbeddingResponse)
def embed(payload: EmbeddingRequest) -> EmbeddingResponse:
    from models import EmbeddingItem

    items = [EmbeddingItem(text=t, vector=providers.embedding.embed(t)) for t in payload.texts]
    return EmbeddingResponse(model=providers.embedding.model, items=items)


@router.post("/reindex-business", response_model=ReindexResponse)
def reindex_business(payload: ReindexRequest) -> ReindexResponse:
    docs = rag_service.documents
    return ReindexResponse(business_id=payload.business_id, indexed_documents=len(docs), status="ok")


@router.post("/voice-to-text", response_model=VoiceResponse)
async def voice_to_text(file: UploadFile = File(...)) -> VoiceResponse:
    text = await providers.whisper.transcribe(file)
    return VoiceResponse(text=text)
