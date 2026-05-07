class IntentService:
    def detect(self, text: str) -> tuple[str, float]:
        lower = text.lower()

        if any(k in lower for k in ["refund", "return", "money back", "রিফান্ড", "ফেরত"]):
            return "refund_request", 0.92
        if any(k in lower for k in ["price", "cost", "দাম"]):
            return "price_query", 0.88
        if any(k in lower for k in ["order", "অর্ডার"]):
            return "order_status", 0.9
        if any(k in lower for k in ["human", "agent", "support", "handover", "মানুষ", "এজেন্ট"]):
            return "human_handover", 0.92
        if any(k in lower for k in ["delivery", "shipping", "arrive", "ডেলিভারি"]):
            return "delivery_query", 0.86
        return "general_query", 0.7
