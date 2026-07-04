from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.routes import cancer, chatbot, period, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="She Check API",
    description="Women's health platform — cancer detection, health chatbot, period tracker",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(cancer.router,  prefix="/api/cancer",  tags=["Cancer Detection"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Health Chatbot"])
app.include_router(period.router,  prefix="/api/period",  tags=["Period Tracker"])


@app.get("/", tags=["Health"])
async def root():
    return {"message": "She Check API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}