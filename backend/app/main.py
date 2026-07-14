from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cores.config import settings
from app.api.routes import health, auth, upload, chat
from app.services.vector_service import ensure_collection_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup — before the app accepts any requests
    print("Starting up — initializing Qdrant collection...")
    ensure_collection_exists()
    print("Qdrant ready")
    yield
    # Anything after yield runs on shutdown (cleanup)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


@app.get("/")
def root():
    return {"message": "Finance RAG Chatbot API"}