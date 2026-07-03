from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def check_health():
    return {
        "status": 200,
        "message":"Working Fine!"
    }