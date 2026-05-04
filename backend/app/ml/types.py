from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelBundle:
    disease: str
    model_name: str
    model: object
    feature_names: list[str]
    explainer: object
