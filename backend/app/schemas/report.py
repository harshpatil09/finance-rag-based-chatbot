from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # replaces class Config

    id: str
    filename: str
    file_size: int
    company_name: str | None
    quarter: str | None
    status: str
    uploaded_at: datetime