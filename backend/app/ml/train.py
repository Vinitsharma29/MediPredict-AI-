from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.types import ModelBundle

DATA_DIR = Path(__file__).resolve().parent / "data"
MODELS_DIR = Path(__file__).resolve().parent / "models"


def _data_path(disease: str) -> Path:
    if disease == "heart":
        return DATA_DIR / "heart.csv"
    if disease == "diabetes":
        return DATA_DIR / "diabetes.csv"
    raise ValueError("unknown disease")


def _model_path(disease: str) -> Path:
    return MODELS_DIR / f"{disease}_rf.joblib"


def _load_dataset(disease: str):
    path = _data_path(disease)
    if not path.exists():
        raise RuntimeError(
            f"Dataset missing: {path}. Place a real Kaggle/UCI CSV there (see {DATA_DIR / 'README.md'})."
        )

    df = pd.read_csv(path)

    if disease == "heart":
        if "target" not in df.columns:
            raise RuntimeError("heart.csv must include a 'target' column")
        y = df["target"].astype(int)
        X = df.drop(columns=["target"])
        return X, y

    if disease == "diabetes":
        for label_col in ("Outcome", "outcome", "target"):
            if label_col in df.columns:
                y = df[label_col].astype(int)
                X = df.drop(columns=[label_col])
                return X, y
        raise RuntimeError("diabetes.csv must include label column Outcome/outcome/target")

    raise ValueError("unknown disease")


def train_and_persist(disease: str) -> ModelBundle:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = _load_dataset(disease)
    feature_names = list(X.columns)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=500,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipeline.fit(X_train, y_train)

    try:
        probs = pipeline.predict_proba(X_test)[:, 1]
        auc = float(roc_auc_score(y_test, probs))
    except Exception:
        auc = -1.0

    joblib.dump({"pipeline": pipeline, "feature_names": feature_names, "auc": auc}, _model_path(disease))

    rf = pipeline.named_steps["rf"]
    explainer = shap.TreeExplainer(rf)

    return ModelBundle(
        disease=disease,
        model_name=f"rf_v1_auc_{auc:.3f}" if auc >= 0 else "rf_v1",
        model=pipeline,
        feature_names=feature_names,
        explainer=explainer,
    )
