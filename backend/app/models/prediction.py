from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)

    disease: Mapped[str] = mapped_column(String(50), index=True)  # heart | diabetes
    model_name: Mapped[str] = mapped_column(String(100))
    risk_level: Mapped[str] = mapped_column(String(10))
    probability: Mapped[float]

    features: Mapped[dict] = mapped_column(JSON)
    feature_importance: Mapped[dict] = mapped_column(JSON)
    shap_values: Mapped[dict] = mapped_column(JSON)
    recommendations: Mapped[dict] = mapped_column(JSON)

    doctor_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctor_decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
