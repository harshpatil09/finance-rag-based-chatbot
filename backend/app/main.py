from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Finance RAG Chatbot",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Finance RAG Chatbot API Running"
    }