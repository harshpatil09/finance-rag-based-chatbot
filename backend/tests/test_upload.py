import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.cores.dependencies import get_current_user
from app.models.user import User
from app.models.report import ReportStatus


# Mock the current user (no DB needed for auth)
def mock_current_user():
    return User(id="test-user-id", email="test@test.com", role="admin")

app.dependency_overrides[get_current_user] = mock_current_user
client = TestClient(app)


def make_pdf_bytes() -> bytes:
    return b"%PDF-1.4 1 0 obj<</Type /Catalog>>endobj"


# Fake report object that save_upload would normally return
def make_fake_report():
    from app.models.report import Report
    r = Report()
    r.id = "fake-report-id"
    r.filename = "apple_q3.pdf"
    r.stored_filename = "some-uuid.pdf"
    r.file_size = 40
    r.company_name = "Apple"
    r.quarter = "Q3 2024"
    r.status = ReportStatus.uploaded
    r.uploaded_by = "test-user-id"
    r.uploaded_at = datetime.now(timezone.utc)
    return r


@patch("app.api.routes.upload.save_upload", new_callable=AsyncMock)
def test_upload_valid_pdf(mock_save):
    """Happy path — valid PDF should return 201 with metadata."""
    mock_save.return_value = make_fake_report()

    response = client.post(
        "/api/v1/upload",
        files={"file": ("apple_q3.pdf", make_pdf_bytes(), "application/pdf")},
        data={"company_name": "Apple", "quarter": "Q3 2024"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "apple_q3.pdf"
    assert body["company_name"] == "Apple"
    assert body["status"] == "uploaded"
    mock_save.assert_called_once()  # verify service was actually called


def test_upload_rejects_non_pdf():
    """Should return 400 if the file is not a PDF."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("report.txt", b"not a pdf", "text/plain")},
        data={"company_name": "Apple", "quarter": "Q3 2024"}
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_upload_requires_company_name():
    """Should return 422 if company_name is missing."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("apple_q3.pdf", make_pdf_bytes(), "application/pdf")},
        data={"quarter": "Q3 2024"}
    )
    assert response.status_code == 422