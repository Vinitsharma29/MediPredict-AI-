from __future__ import annotations

from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "app" / "ml" / "data"

HEART_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
DIAB_URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Heart: processed.cleveland.data -> heart.csv (binary target)
    heart = requests.get(HEART_URL, timeout=60)
    heart.raise_for_status()
    out_heart = DATA_DIR / "heart.csv"
    header = "age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target\n"
    lines = []
    lines.append(header)
    for raw in heart.text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(",")
        if len(parts) != 14:
            continue
        if "?" in parts:
            continue
        num = int(float(parts[13]))
        parts[13] = "1" if num > 0 else "0"
        lines.append(",".join(parts) + "\n")
    out_heart.write_text("".join(lines), encoding="utf-8")

    # Diabetes: add header then append raw
    diab = requests.get(DIAB_URL, timeout=60)
    diab.raise_for_status()
    out_diab = DATA_DIR / "diabetes.csv"
    header2 = "Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age,Outcome\n"
    out_diab.write_text(header2 + diab.text, encoding="utf-8")

    print(f"Saved: {out_heart}")
    print(f"Saved: {out_diab}")


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
