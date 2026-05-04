from __future__ import annotations

from typing import Any

import numpy as np

from app.ml.registry import get_bundle


def _risk_from_prob(p: float) -> str:
    if p < 0.33:
        return "Low"
    if p < 0.66:
        return "Medium"
    return "High"


def _top_features(feature_names: list[str], weights: np.ndarray, x_row: np.ndarray, k: int = 8) -> dict:
    order = np.argsort(np.abs(weights))[::-1][:k]
    items = []
    for i in order:
        items.append(
            {
                "feature": feature_names[int(i)],
                "shap": float(weights[int(i)]),
                "value": float(x_row[int(i)]),
            }
        )
    return {"top": items}


def predict(disease: str, features: dict[str, Any]) -> dict[str, Any]:
    bundle = get_bundle(disease)
    fn = bundle.feature_names

    x = np.array([[float(features.get(f, 0.0)) for f in fn]], dtype=float)

    pipeline = bundle.model
    prob = float(pipeline.predict_proba(x)[0, 1])
    risk = _risk_from_prob(prob)

    # Explain: Prefer SHAP (local), fallback to RF global feature importances.
    fi = {"top": []}
    shap_out = {"values": {}}

    rf = pipeline.named_steps.get("rf")

    try:
        scaled = pipeline.named_steps["scaler"].transform(x)
        shap_vals = bundle.explainer.shap_values(scaled)
        if isinstance(shap_vals, list):
            shap_row = np.array(shap_vals[1][0], dtype=float)
        else:
            # Newer shap may return (n_samples, n_features)
            arr = np.array(shap_vals, dtype=float)
            shap_row = arr[0] if arr.ndim == 2 else arr
        fi = _top_features(fn, shap_row, x[0])
        shap_out = {"values": {fn[i]: float(shap_row[i]) for i in range(len(fn))}}
    except Exception:
        try:
            if rf is not None and hasattr(rf, "feature_importances_"):
                imp = np.array(getattr(rf, "feature_importances_"), dtype=float)
                fi = _top_features(fn, imp, x[0])
        except Exception:
            pass

    return {
        "disease": disease,
        "model_name": bundle.model_name,
        "probability": prob,
        "risk_level": risk,
        "feature_importance": fi,
        "shap_values": shap_out,
<<<<<<< HEAD
    }
=======
    }
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
