from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), index=True)
    age: Mapped[int] = mapped_column(index=True)
    gender: Mapped[str] = mapped_column(String(20), index=True)

    symptoms: Mapped[dict] = mapped_column(JSON)
    vitals: Mapped[dict] = mapped_column(JSON)

<<<<<<< HEAD
    medical_history_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
=======
    medical_history_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
