from __future__ import annotations

from app.ml.train import train_and_persist
from app.ml.types import ModelBundle

_REGISTRY: dict[str, ModelBundle] = {}


def ensure_models_ready() -> None:
    for disease in ("heart", "diabetes"):
        if disease in _REGISTRY:
            continue
        bundle = train_and_persist(disease)
        _REGISTRY[disease] = bundle


def get_bundle(disease: str) -> ModelBundle:
    disease = disease.lower().strip()
    if disease not in _REGISTRY:
        ensure_models_ready()
    if disease not in _REGISTRY:
        raise ValueError(f"Unsupported disease: {disease}")
<<<<<<< HEAD
    return _REGISTRY[disease]
=======
    return _REGISTRY[disease]
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
