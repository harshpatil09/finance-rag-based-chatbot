from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    report_id: str
    top_k: int = 5


class SourceChunk(BaseModel):
    rank: int
    score: float
    section: str
    page: int | None
    chunk_type: str
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    question: str