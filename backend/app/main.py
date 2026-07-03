from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cores.config import settings
from app.api.routes import health, auth

app = FastAPI(title=settings.PROJECT_NAME)

# CORS must be added BEFORE routes — order matters in FastAPI middleware
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

@app.get("/")
def root():
    return {"message": "Finance RAG Chatbot API"}