class IntentService:
    def detect(self, text: str) -> tuple[str, float]:
        lower = text.lower()

        if any(k in lower for k in ["refund", "return", "money back"]):
            return "refund", 0.9
        if any(k in lower for k in ["price", "cost", "plan", "subscription"]):
            return "pricing", 0.85
        if any(k in lower for k in ["human", "agent", "support", "handover"]):
            return "human_handover", 0.92
        if any(k in lower for k in ["delivery", "shipping", "arrive"]):
            return "delivery", 0.83
        return "general", 0.65
