# SupportBond AI / Shobar Shonge

AI Customer Support SaaS + Multi-vendor Marketplace Support Platform.

## 1) Project Overview
This project combines:
- AI customer support (inbox, tickets, chatbot, FAQ, products, integrations)
- Multi-vendor marketplace operations (vendors, orders, commissions, payouts, vendor panel)

## 2) Folder Structure
- `frontend/` React + Vite dashboard and routes
- `backend/` Django + DRF APIs
- `ai_service/` FastAPI AI service
- `docker-compose.yml` local container orchestration

## 3) Requirements
- Python 3.10+
- Node.js 18+
- npm 9+
- Optional: Docker Desktop
- Optional: Redis/PostgreSQL (SQLite fallback available)

## 4) Environment Setup
Create local env files from examples:
- `frontend/.env.example`
- `backend/.env.example`
- `ai_service/.env.example`

## 5) Frontend Run
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Build:
```powershell
npm run build
```

## 6) Backend Run
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

## 7) AI Service Run
```powershell
cd ai_service
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

## 8) Docker Run
```powershell
docker compose up --build
```
Then:
```powershell
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo
```

## 9) Database Migration
```powershell
cd backend
python manage.py migrate
```

## 10) Demo Seed
```powershell
cd backend
python manage.py seed_demo
```

## 11) Demo Credentials
- `marketplace@supportbond.ai / password123`
- `vendor1@supportbond.ai / password123`
- `vendor2@supportbond.ai / password123`
- `agent@supportbond.ai / password123`
- `owner@supportbond.ai / password123`

## 12) API Base URLs
- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- AI Service: `http://127.0.0.1:8001`

## 13) API Docs URL
- Schema: `http://127.0.0.1:8000/api/schema/`
- Swagger: `http://127.0.0.1:8000/api/docs/`

## 14) Troubleshooting
### CORS error
- Ensure `CORS_ALLOWED_ORIGINS` includes frontend URL
- Or `CORS_ALLOW_ALL_ORIGINS=1` for local dev

### Backend not reachable
- Check `python manage.py runserver 127.0.0.1:8000`
- Check no port conflict on `8000`

### Frontend blank page
- Run from `frontend` folder only
- Ensure `VITE_API_BASE_URL=http://127.0.0.1:8000`

### Migration error
- Run `python manage.py makemigrations`
- Then `python manage.py migrate`

### AI service down
- Start uvicorn command in `ai_service`
- Django chatbot has fallback safe reply

### Redis not running
- Celery/real-time background tasks may degrade
- Core HTTP API can still run in dev mode

### PostgreSQL password error
- Use SQLite fallback with `DATABASE_URL=sqlite:///db.sqlite3`

## 15) Multi-vendor Notes
Implemented API groups:
- Marketplace owner: vendors, categories, product moderation, orders, commissions, payouts, analytics
- Vendor APIs: dashboard, products, orders, tickets, FAQs, payouts, settings
- Storefront test APIs: order create + order lookup

## 16) Known Limitations
- Vendor/marketplace frontend pages are functional but minimal (not fully polished UX)
- Some legacy endpoints still use owner-centric logic; core flows are stabilized but can be hardened further with stricter RBAC classes
- Bank account info is stored in JSON; field-level encryption is recommended for production

## 17) Verified Commands
- `python manage.py check` ?
- `python manage.py migrate` ?
- `python manage.py seed_demo` ?
- `python manage.py test` ?
- `npm run build` ?
- `ai_service import` ?
