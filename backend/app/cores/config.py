from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # add this

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
        )  # replaces inner class Config

    PROJECT_NAME: str = "Finance RAG Chatbot"
    ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50
    
    # Qdrant vector DB
    QDRANT_PATH: str = "./qdrant_storage"
    QDRANT_COLLECTION: str = "finance_chunks"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

settings = Settings()