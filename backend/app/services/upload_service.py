import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.cores.config import settings
from app.models.report import Report, ReportStatus


ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def ensure_upload_dir():
    """Create uploads folder if it doesn't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


async def save_upload(
    file: UploadFile,
    company_name: str,
    quarter: str,
    user_id: str,
    db: Session
) -> Report:
    # 1. Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # 2. Read file into memory to check size
    #    We read in chunks to avoid loading huge files all at once
    contents = b""
    chunk_size = 1024 * 1024  # 1MB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        contents += chunk
        if len(contents) > MAX_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB"
            )

    # 3. Generate a safe filename — never trust user input for filenames
    stored_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    # 4. Write to disk asynchronously (non-blocking)
    ensure_upload_dir()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    # 5. Save metadata to MySQL
    report = Report(
        filename=file.filename,
        stored_filename=stored_filename,
        file_size=len(contents),
        company_name=company_name,
        quarter=quarter,
        status=ReportStatus.uploaded,
        uploaded_by=user_id
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report