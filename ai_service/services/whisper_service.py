from fastapi import UploadFile


class WhisperService:
    async def transcribe(self, file: UploadFile) -> str:
        content = await file.read()
        if not content:
            return ""
        # Placeholder implementation for MVP wiring.
        return f"Transcription placeholder for file '{file.filename}' ({len(content)} bytes)."
