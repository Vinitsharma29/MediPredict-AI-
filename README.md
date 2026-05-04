# MediPredict AI (Hackathon MVP)

Production-style, full‑stack clinical decision support web app with **real ML predictions** (scikit‑learn) + **Explainable AI (SHAP)**, doctor workflow, demo mode, analytics, and MySQL persistence.

## Tech
- Frontend: React + Vite, MUI, Recharts
- Backend: FastAPI, SQLAlchemy, MySQL, JWT auth
- ML: scikit‑learn + SHAP (heart disease + diabetes)

## Quick start (Docker)
1) Install Docker Desktop
2) From this folder:
```powershell
cd "C:\Users\ASUS\Documents\New project\MediPredictAI"
docker compose up --build
```
3) Open:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

## Quick start (No Docker)
### MySQL
Create DB + user, then run:
```sql
CREATE DATABASE medipredict CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Backend
```powershell
cd "C:\Users\ASUS\Documents\New project\MediPredictAI\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd "C:\Users\ASUS\Documents\New project\MediPredictAI\frontend"
npm install
npm run dev
```

## Default demo accounts
- Doctor: `doctor@medipredict.ai` / `Doctor@123`
- Patient: `patient@medipredict.ai` / `Patient@123`

## MySQL CLI access (required)
```powershell
mysql -h 127.0.0.1 -P 3306 -u medipredict -p medipredict
```

## Notes
- ML models train automatically on first backend start using bundled datasets in `backend/app/ml/data/`.
<<<<<<< HEAD
- Uploaded reports stored in `backend/storage/` and indexed in MySQL.

## Datasets (required for real AI)
Run powershell -ExecutionPolicy Bypass -File .\scripts\fetch_datasets.ps1 to download real heart/diabetes datasets into ackend/app/ml/data/ (or place Kaggle CSVs manually).
=======
- Uploaded reports stored in `backend/storage/` and indexed in MySQL.

## Datasets (required for real AI)
Run powershell -ExecutionPolicy Bypass -File .\scripts\fetch_datasets.ps1 to download real heart/diabetes datasets into ackend/app/ml/data/ (or place Kaggle CSVs manually).
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
