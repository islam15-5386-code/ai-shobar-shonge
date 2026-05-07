from fastapi import APIRouter

from models import SentimentRequest, SentimentResponse
from services import SentimentService

router = APIRouter()
sentiment_service = SentimentService()


@router.post("/", response_model=SentimentResponse)
def detect_sentiment(payload: SentimentRequest) -> SentimentResponse:
    sentiment, score = sentiment_service.analyze(payload.text)
    return SentimentResponse(sentiment=sentiment, score=round(score, 3))
