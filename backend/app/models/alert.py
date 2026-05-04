from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    risk_level: Mapped[str] = mapped_column(String(10))
    probability: Mapped[float]

<<<<<<< HEAD
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)  # active | resolved
=======
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)  # active | resolved
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
