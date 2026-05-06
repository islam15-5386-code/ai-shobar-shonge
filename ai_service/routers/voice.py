from fastapi import APIRouter, File, UploadFile

from models import VoiceResponse
from services.runtime import providers

router = APIRouter()


@router.post("/transcribe", response_model=VoiceResponse)
async def transcribe_voice(file: UploadFile = File(...)) -> VoiceResponse:
    text = await providers.whisper.transcribe(file)
    return VoiceResponse(text=text)
