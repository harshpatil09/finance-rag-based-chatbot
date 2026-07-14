from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.cores.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import query_report, query_report_stream

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Non-streaming chat endpoint.
    Returns complete answer + sources in one response.
    Use this for testing in Swagger.
    """
    try:
        result = query_report(
            question=payload.question,
            report_id=payload.report_id,
            top_k=payload.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Streaming chat endpoint using Server-Sent Events.
    Angular EventSource connects here and receives tokens as they arrive.
    The Authorization header is passed as a query param for SSE
    since EventSource doesn't support custom headers natively.
    """
    try:
        return StreamingResponse(
            query_report_stream(
                question=payload.question,
                report_id=payload.report_id,
                top_k=payload.top_k
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"   # prevents nginx from buffering the stream
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))