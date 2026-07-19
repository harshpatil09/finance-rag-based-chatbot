from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cores.database import get_db
from app.cores.dependencies import get_current_user
from app.models.user import User
from app.models.insight import ReportInsight
from app.schemas.insight import InsightResponse
from app.services.insights_service import extract_insights

router = APIRouter()


@router.get("/insights/{report_id}", response_model=InsightResponse)
def get_insights(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get extracted KPIs for a report."""
    insight = db.query(ReportInsight).filter(
        ReportInsight.report_id == report_id
    ).first()

    if not insight:
        raise HTTPException(status_code=404, detail="Insights not found for this report")

    return insight


@router.post("/insights/{report_id}/refresh", response_model=InsightResponse)
def refresh_insights(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Re-extract insights for a report — useful if extraction failed initially."""
    try:
        insight = extract_insights(report_id, db)
        return insight
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))