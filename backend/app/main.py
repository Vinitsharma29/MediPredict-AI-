from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.startup import init_app
from app.routers import analytics, alerts, auth, chat, doctor, patients, predictions, reports


def create_app() -> FastAPI:
    app = FastAPI(
        title="MediPredict AI API",
        version="1.0.0",
        description="Clinical decision support backend (FastAPI + MySQL + scikit-learn + SHAP).",
    )

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(patients.router, prefix="/patients", tags=["patients"])
    app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
    app.include_router(reports.router, prefix="/reports", tags=["reports"])
    app.include_router(doctor.router, prefix="/doctor", tags=["doctor"])
    app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

    init_app(app)
    return app


app = create_app()
