from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500))
    mimetype: Mapped[str] = mapped_column(String(100))

<<<<<<< HEAD
    extracted_text_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
=======
    extracted_text_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
