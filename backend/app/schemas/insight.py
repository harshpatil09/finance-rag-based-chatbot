from pydantic import BaseModel
from datetime import datetime


class InsightResponse(BaseModel):
    report_id: str
    total_revenue: float | None
    net_income: float | None
    gross_profit: float | None
    operating_income: float | None
    eps_basic: float | None
    eps_diluted: float | None
    gross_margin: float | None
    net_margin: float | None
    total_assets: float | None
    total_liabilities: float | None
    total_equity: float | None
    operating_cash_flow: float | None
    extracted_at: datetime

    model_config = {"from_attributes": True}