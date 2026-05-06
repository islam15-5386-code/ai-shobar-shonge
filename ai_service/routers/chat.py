from fastapi import APIRouter

from models import ChatRequest, ChatResponse
from services import IntentService, RAGService, SentimentService
from services.runtime import providers

router = APIRouter()

intent_service = IntentService()
sentiment_service = SentimentService()
rag_service = RAGService(embedding_provider=providers.embedding)


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    intent, intent_conf = intent_service.detect(payload.message)
    sentiment, sent_score = sentiment_service.analyze(payload.message)

    docs = rag_service.retrieve(payload.message)
    context = [str(d.get("text", "")) for d in docs if d.get("text")]
    reply = providers.llm.generate_reply(payload.message, context=context, locale=payload.locale)

    confidence = round((intent_conf + sent_score) / 2, 3)
    return ChatResponse(
        reply=reply,
        intent=intent,
        sentiment=sentiment,
        confidence=confidence,
        context=context,
    )
