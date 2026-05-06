from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    business_id: int | None = None
    locale: str = "en"


class ChatResponse(BaseModel):
    reply: str
    intent: str
    sentiment: str
    confidence: float
    context: list[str] = []


class IntentRequest(BaseModel):
    text: str = Field(..., min_length=1)


class IntentResponse(BaseModel):
    intent: str
    confidence: float


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SentimentResponse(BaseModel):
    sentiment: str
    score: float


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)


class EmbeddingItem(BaseModel):
    text: str
    vector: list[float]


class EmbeddingResponse(BaseModel):
    model: str
    items: list[EmbeddingItem]


class VoiceResponse(BaseModel):
    text: str
