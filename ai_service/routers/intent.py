from fastapi import APIRouter

from models import IntentRequest, IntentResponse
from services import IntentService

router = APIRouter()
intent_service = IntentService()


@router.post("/", response_model=IntentResponse)
def detect_intent(payload: IntentRequest) -> IntentResponse:
    intent, confidence = intent_service.detect(payload.text)
    return IntentResponse(intent=intent, confidence=round(confidence, 3))
