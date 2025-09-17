# FraudShield - ML-based Credit Card Fraud Detection

A production-ready fraud detection system with FastAPI backend (ML training/inference) and a React (CRA) frontend.

## One-click run (Docker)

Requirements:
- Docker and Docker Compose installed

Steps:
1. (Optional) Create a `.env` file in the repo root to override defaults:
```
MONGO_URL=mongodb://mongo:27017
DB_NAME=fraudshield
REACT_APP_BACKEND_URL=http://localhost:8000
```
2. Start all services:
```
docker compose up --build
```
3. Open the app:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

The backend mounts `./data` into the container at `/app/data` so trained models and sample data persist.

## Local development (without Docker)

## Deploy frontend to GitHub Pages

We added a GitHub Actions workflow at `.github/workflows/pages.yml` that builds the React app and deploys it to GitHub Pages.

Steps:
1. Deploy the backend somewhere public (e.g., Render). Note the base URL (e.g., `https://your-backend.onrender.com`).
2. In GitHub → your repo → Settings → Secrets and variables → Actions → Variables → Add `BACKEND_URL` with the backend URL.
3. In GitHub → Settings → Pages → Source: GitHub Actions.
4. Push to `main` or manually run the workflow in the Actions tab.
5. Your site is available at the URL shown in Settings → Pages (typically `https://<user>.github.io/<repo>/`).

Backend:
```
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r backend/requirements.txt
set MONGO_URL=mongodb://localhost:27017
set DB_NAME=fraudshield
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```
cd frontend
set REACT_APP_BACKEND_URL=http://localhost:8000
yarn install
yarn start
```

## Features
- Train Logistic Regression, Random Forest, XGBoost, and Neural Network
- Class imbalance handling (SMOTE / undersampling)
- Save and auto-load latest trained models/metrics
- Single and batch prediction (CSV upload)
- Model metrics and feature-importance endpoints

## Notes
- Dataset path inside containers: `/app/data/creditcard.csv`. Add the file under `data/creditcard.csv` locally if you have it; otherwise use sample inputs in the UI.
- MongoDB is optional; endpoints degrade gracefully if `MONGO_URL` is not set.
- Latest models auto-load on backend startup if found in `data/models`.
