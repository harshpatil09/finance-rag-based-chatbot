from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.cores.database import get_db
from app.cores.dependencies import get_current_user
from app.models.user import User
from app.services.upload_service import save_upload
from app.services.processing_service import process_report
from app.schemas.report import ReportResponse

router = APIRouter()


@router.post("/upload", response_model=ReportResponse, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    quarter: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # protected
):
    """
    Upload a quarterly report PDF.
    Requires a valid JWT in the Authorization header.
    Accepts multipart/form-data with: file, company_name, quarter.
    """
    report = await save_upload(
        file=file,
        company_name=company_name,
        quarter=quarter,
        user_id=current_user.id,
        db=db
    )
    return report

@router.post("/process/{report_id}")
def trigger_processing(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger document parsing pipeline for an uploaded report.
    In M6 this will become async (background task).
    For now it runs synchronously so we can verify it works.
    """
    try:
        result = process_report(report_id, db)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")