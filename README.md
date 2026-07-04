# She Check — Women's Health Platform

A full-stack health platform with three core modules:
1. **Breast Cancer Detection** — ML model via image or clinical parameters
2. **Women's Health Chatbot** — Powered by Gemini 1.5 Flash
3. **Period Tracker** — Cycle prediction + phase advisories

## Project Structure

```
she-check/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + lifespan
│   │   ├── core/
│   │   │   ├── config.py        # Settings (env vars)
│   │   │   └── security.py      # JWT auth + password hashing
│   │   ├── db/
│   │   │   └── mongodb.py       # Motor async client + collections
│   │   ├── models/              # MongoDB document schemas
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── api/routes/          # FastAPI routers
│   │   │   ├── auth.py          # /api/auth — register, login
│   │   │   ├── cancer.py        # /api/cancer — predict, history
│   │   │   ├── chatbot.py       # /api/chatbot — chat, history
│   │   │   └── period.py        # /api/period — log, fetch
│   │   ├── services/            # Business logic
│   │   │   ├── cancer_service.py
│   │   │   ├── chatbot_service.py
│   │   │   └── period_service.py
│   │   └── ml/                  # ML model files (add .pkl / .pth here)
│   ├── requirements.txt
│   ├── .env.example
│   └── run.sh
└── frontend/                    # React / Next.js (to be scaffolded)
```

## Quick Start

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add your GEMINI_API_KEY
./run.sh
```

API docs available at: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| POST   | /api/auth/register              | Register new user            |
| POST   | /api/auth/login                 | Login, get JWT               |
| POST   | /api/cancer/predict/parameters  | Predict from clinical params |
| POST   | /api/cancer/predict/image       | Predict from mammogram image |
| GET    | /api/cancer/history             | User's past results          |
| POST   | /api/chatbot/chat               | Send message to chatbot      |
| GET    | /api/chatbot/history/{id}       | Fetch chat session           |
| POST   | /api/period/log                 | Log cycles + get prediction  |
| GET    | /api/period/log                 | Fetch saved period log       |

## Next Steps
- [ ] Train cancer detection ML model (Wisconsin Breast Cancer dataset)
- [ ] Fine-tune CNN on mammogram dataset (CBIS-DDSM)
- [ ] Build React frontend
- [ ] Add RAG to chatbot (medical knowledge base)
- [ ] Deploy (Railway / Render for backend, Vercel for frontend)
