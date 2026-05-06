from fastapi import APIRouter, File, UploadFile

from models import VoiceResponse
from services import WhisperService

router = APIRouter()
whisper_service = WhisperService()


@router.post("/transcribe", response_model=VoiceResponse)
async def transcribe_voice(file: UploadFile = File(...)) -> VoiceResponse:
    text = await whisper_service.transcribe(file)
    return VoiceResponse(text=text)
