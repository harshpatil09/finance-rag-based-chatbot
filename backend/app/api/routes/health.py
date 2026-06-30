from fastapi import APIRouter

router = APIRouter(
    prefix='/api/v1'
)

@router.get("/health")
def check_health():
    return {
        "status": 200,
        "message":"Working Fine!"
    }