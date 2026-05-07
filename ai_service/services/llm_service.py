import json
from urllib import error, request

from config import settings


class LLMService:
    def generate_reply(self, message: str, context: list[str], locale: str = "en") -> str:
        if not context:
            base = "Thanks for your message. I could not find a direct answer yet."
        else:
            base = f"Based on available knowledge: {context[0]}"

        if locale.lower().startswith("bn"):
            return f"আপনার বার্তার জন্য ধন্যবাদ। {base}"
        return base

    @property
    def model_name(self) -> str:
        return settings.llm_model


class GeminiLLMService(LLMService):
    def generate_reply(self, message: str, context: list[str], locale: str = "en") -> str:
        if not settings.gemini_api_key:
            return super().generate_reply(message=message, context=context, locale=locale)

        prompt_locale = "Bangla" if locale.lower().startswith("bn") else "English"
        context_block = "\n".join(f"- {line}" for line in context[:5]) if context else "- No verified business context found"
        prompt = (
            "You are a customer support assistant for a Bangladeshi business.\n"
            f"Reply only in {prompt_locale}.\n"
            "Do not invent policies. If information is unknown, politely suggest human support handover.\n"
            f"Customer message: {message}\n"
            f"Business context:\n{context_block}"
        )

        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 300},
        }
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and parts[0].get("text"):
                    return str(parts[0]["text"]).strip()
        except (error.URLError, TimeoutError, ValueError, KeyError):
            return super().generate_reply(message=message, context=context, locale=locale)

        return super().generate_reply(message=message, context=context, locale=locale)

    @property
    def model_name(self) -> str:
        return settings.gemini_model
