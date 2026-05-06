from fastapi import FastAPI

from routers.chat import router as chat_router
from routers.embeddings import router as embeddings_router
from routers.intent import router as intent_router
from routers.sentiment import router as sentiment_router
from routers.voice import router as voice_router

app = FastAPI(title="AI Service", version="1.0.0")

app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(intent_router, prefix="/intent", tags=["intent"])
app.include_router(sentiment_router, prefix="/sentiment", tags=["sentiment"])
app.include_router(embeddings_router, prefix="/embeddings", tags=["embeddings"])
app.include_router(voice_router, prefix="/voice", tags=["voice"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
