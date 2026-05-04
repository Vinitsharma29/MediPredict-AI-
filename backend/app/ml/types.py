from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelBundle:
    disease: str
    model_name: str
    model: object
    feature_names: list[str]
<<<<<<< HEAD
    explainer: object
=======
    explainer: object
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
