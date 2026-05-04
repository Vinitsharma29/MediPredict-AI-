# ML Datasets (required)

MediPredict AI trains *real* scikit-learn models on first backend start. To keep the demo fully offline, commit the datasets below into this folder.

## Files

1) `heart.csv`
- Source: Kaggle/UCI-style Heart Disease dataset
- Must include a binary label column named `target` (0/1)

2) `diabetes.csv`
- Source: Kaggle/UCI-style Pima Indians Diabetes dataset
- Must include a binary label column named `Outcome` (0/1) (or `outcome` or `target`)

## Quick fetch (online)
From repo root:

- PowerShell:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\fetch_datasets.ps1`

<<<<<<< HEAD
If your dataset schemas differ, adjust the column names or update `backend/app/ml/train.py`.
=======
If your dataset schemas differ, adjust the column names or update `backend/app/ml/train.py`.
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
