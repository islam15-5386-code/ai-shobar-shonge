# SupportBond AI

Production-ready AI Customer Support SaaS for Bangladeshi businesses.

## Architecture
- Frontend: Lovable-generated React app (`frontend`)
- Backend API: Django + DRF (`backend`)
- AI Service: FastAPI (`ai_service`)
- DB: PostgreSQL (+ pgvector image)
- Cache/Queue: Redis + Celery
- Realtime: Django Channels

## Core Features
- JWT auth: register/login/refresh/logout/me
- Multi-tenant business isolation (owner/manager/agent)
- FAQ + Product knowledge base
- Website chatbot + AI gateway
- Messenger + WhatsApp webhooks
- Ticketing + human handover
- Billing plans + usage limits
- Analytics + CSV export
- GPU-ready AI service with CPU fallback

## Docker Setup
1. `docker compose up --build`
2. `docker compose exec backend python manage.py migrate`
3. `docker compose exec backend python manage.py seed_demo`

## Local Backend Setup
1. `cd backend`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values
4. `python manage.py migrate`
5. `python manage.py runserver`

## Local AI Service Setup
1. `cd ai_service`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload --port 8001`

## Environment Variables
See `backend/.env.example` and `docker-compose.yml`.
Important:
- `AI_SERVICE_URL`
- `DB_*`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

AI service:
- `AI_MODE=cpu|gpu`
- `LLM_PROVIDER`, `EMBEDDING_PROVIDER`, `WHISPER_PROVIDER`
- `CUDA_DEVICE`

## API Docs
- OpenAPI Schema: `http://localhost:8000/api/schema/`
- Swagger UI: `http://localhost:8000/api/docs/`

## Demo Credentials
- `owner@supportbond.ai / password123`
- `agent@supportbond.ai / password123`

## Messenger/WhatsApp Setup Notes
- Messenger setup: `/api/integrations/messenger/setup/`
- Messenger webhook: `/api/integrations/messenger/webhook/`
- WhatsApp setup: `/api/integrations/whatsapp/setup/`
- WhatsApp webhook: `/api/integrations/whatsapp/webhook/`

## GPU Notes
- `/ai/health` returns `cuda_available`
- If CUDA/model unavailable, service falls back to CPU/mock behavior

## Troubleshooting
- Run checks: `python backend/manage.py check`
- Run tests: `python backend/manage.py test`
- If JWT warnings appear, use longer secret key (`DJANGO_SECRET_KEY` >= 32 chars)
