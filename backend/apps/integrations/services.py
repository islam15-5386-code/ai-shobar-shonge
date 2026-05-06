import json
import os
import uuid
from urllib import error, request


def send_facebook_reply(page_access_token: str, recipient_psid: str, text: str) -> tuple[bool, str]:
    endpoint = f"https://graph.facebook.com/v21.0/me/messages?access_token={page_access_token}"
    payload = {
        "recipient": {"id": recipient_psid},
        "messaging_type": "RESPONSE",
        "message": {"text": text},
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=12) as resp:
            body = resp.read().decode("utf-8")
            return True, body
    except error.HTTPError as exc:
        return False, exc.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def send_whatsapp_text(access_token: str, phone_number_id: str, to_number: str, text: str) -> tuple[bool, str]:
    endpoint = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=12) as resp:
            return True, resp.read().decode("utf-8")
    except error.HTTPError as exc:
        return False, exc.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def fetch_whatsapp_media_bytes(access_token: str, media_id: str) -> tuple[bytes | None, str]:
    meta_url = f"https://graph.facebook.com/v21.0/{media_id}"
    meta_req = request.Request(meta_url, headers={"Authorization": f"Bearer {access_token}"}, method="GET")
    try:
        with request.urlopen(meta_req, timeout=12) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
        media_url = meta.get("url")
        if not media_url:
            return None, "missing media url"
        media_req = request.Request(media_url, headers={"Authorization": f"Bearer {access_token}"}, method="GET")
        with request.urlopen(media_req, timeout=20) as media_resp:
            return media_resp.read(), ""
    except error.HTTPError as exc:
        return None, exc.read().decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
        return None, str(exc)


def transcribe_audio_with_ai_service(audio_bytes: bytes, filename: str = "voice.ogg") -> tuple[bool, str]:
    base_url = os.getenv("AI_SERVICE_BASE_URL", "").rstrip("/")
    if not base_url:
        return False, "AI_SERVICE_BASE_URL not configured"

    endpoint = f"{base_url}/voice/transcribe"
    boundary = f"----codex-{uuid.uuid4().hex}"
    body = []
    body.append(f"--{boundary}\r\n".encode("utf-8"))
    body.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8")
    )
    body.append(b"Content-Type: audio/ogg\r\n\r\n")
    body.append(audio_bytes)
    body.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    payload = b"".join(body)

    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        text = str(parsed.get("text", "")).strip()
        return (True, text) if text else (False, "empty transcript")
    except Exception as exc:  # pragma: no cover
        return False, str(exc)
