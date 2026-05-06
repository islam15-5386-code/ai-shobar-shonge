from __future__ import annotations

import time

import httpx
from django.conf import settings


def ai_respond(message: str, business_id: int | None = None, locale: str = "en") -> dict:
    url = f"{settings.AI_SERVICE_URL.rstrip('/')}/ai/respond"
    started = time.perf_counter()
    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(url, json={"message": message, "business_id": business_id, "locale": locale})
        latency_ms = int((time.perf_counter() - started) * 1000)
        if response.status_code >= 400:
            return {'ok': False, 'status': 'error', 'latency_ms': latency_ms, 'error': f'HTTP {response.status_code}', 'data': None}
        return {'ok': True, 'status': 'ok', 'latency_ms': latency_ms, 'error': '', 'data': response.json()}
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {'ok': False, 'status': 'timeout', 'latency_ms': latency_ms, 'error': str(exc), 'data': None}
