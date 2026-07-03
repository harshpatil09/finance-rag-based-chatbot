from fastapi import FastAPI
from app.api.routes import health, auth

app = FastAPI(
    title="Finance RAG Chatbot",
    version="1.0.0"
)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def root():
    return {
        "message": "Finance RAG Chatbot API Running"
    }