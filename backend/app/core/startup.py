from fastapi import FastAPI

from app.core.db import engine
from app.ml.registry import ensure_models_ready
from app.models.base import Base
from app.seed import seed_if_needed


def init_app(app: FastAPI) -> None:
    @app.on_event("startup")
    def _startup() -> None:
        Base.metadata.create_all(bind=engine)
        ensure_models_ready()
        seed_if_needed()
