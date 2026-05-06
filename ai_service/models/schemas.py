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


class AIRespondRequest(BaseModel):
    message: str = Field(..., min_length=1)
    business_id: int | None = None
    locale: str = "en"


class AIRespondResponse(BaseModel):
    answer: str
    confidence: float
    intent: str
    sentiment: str
    should_escalate: bool = False
    sources: list[str] = []
    model_name: str = "mock"


class ReindexRequest(BaseModel):
    business_id: int


class ReindexResponse(BaseModel):
    business_id: int
    indexed_documents: int
    status: str
