from config import settings


class LLMService:
    def generate_reply(self, message: str, context: list[str], locale: str = "en") -> str:
        # Local deterministic fallback for environments without external API keys.
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
