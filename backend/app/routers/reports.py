import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.patient import Patient
from app.models.report import Report
from app.models.user import User

router = APIRouter()

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"  # backend/storage


@router.post("/upload/{patient_id}")
def upload_report(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    patient_dir = STORAGE_DIR / f"patient_{patient_id}"
    patient_dir.mkdir(parents=True, exist_ok=True)

    safe_name = file.filename or "report"
    out_name = f"{uuid.uuid4().hex}_{safe_name}"
    out_path = patient_dir / out_name

    with out_path.open("wb") as f:
        f.write(file.file.read())

    rec = Report(
        patient_id=patient_id,
        filename=safe_name,
        stored_path=str(out_path),
        mimetype=file.content_type or "application/octet-stream",
        extracted_text_enc=None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {"id": rec.id, "filename": rec.filename, "mimetype": rec.mimetype}


@router.get("/by-patient/{patient_id}")
def list_reports(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    rows = db.scalars(select(Report).where(Report.patient_id == patient_id).order_by(Report.created_at.desc())).all()
    return [
        {"id": r.id, "filename": r.filename, "mimetype": r.mimetype, "created_at": r.created_at.isoformat()}
        for r in rows
    ]


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Not found")

    patient = db.get(Patient, report.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    path = Path(report.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing")

    return FileResponse(path, media_type=report.mimetype, filename=report.filename)

