class SentimentService:
    NEGATIVE = ["bad", "angry", "terrible", "hate", "worst", "not working", "frustrated"]
    POSITIVE = ["great", "thanks", "awesome", "good", "love", "helpful"]

    def analyze(self, text: str) -> tuple[str, float]:
        lower = text.lower()
        neg = sum(1 for x in self.NEGATIVE if x in lower)
        pos = sum(1 for x in self.POSITIVE if x in lower)

        total = pos + neg
        if total == 0:
            return "neutral", 0.5
        if neg > pos:
            return "negative", min(1.0, 0.5 + (neg / (total * 2)))
        if pos > neg:
            return "positive", min(1.0, 0.5 + (pos / (total * 2)))
        return "neutral", 0.5
