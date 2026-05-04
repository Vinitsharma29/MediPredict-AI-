from pydantic import BaseModel, ConfigDict


class PredictRequest(BaseModel):
    patient_id: int
    disease: str  # heart | diabetes


class PredictionOut(BaseModel):
    # Allow field name `model_name` (pydantic protects `model_` by default)
    model_config = ConfigDict(protected_namespaces=())

    id: int
    patient_id: int
    disease: str
    model_name: str
    risk_level: str
    probability: float
    feature_importance: dict
    shap_values: dict
    recommendations: dict

    alert_flag: bool
<<<<<<< HEAD
    alert_id: int | None = None
=======
    alert_id: int | None = None
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
