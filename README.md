# Life Resume – Behavioral Personality Portfolio

Life Resume analyzes GitHub behavioral signals and builds a personality intelligence profile. It combines data ingestion, feature engineering, personality inference, and a dashboard with a downloadable PDF report.

## Tech Stack
- Backend: FastAPI, MongoEngine, Celery (eager mode)
- ML: scikit-learn, pandas, numpy, lizard
- Frontend: React (Vite), Recharts
- Database: MongoDB
- Auth: JWT + GitHub OAuth

## Setup
1. Clone and enter the repo.
2. Copy `.env.example` to `.env` and fill GitHub OAuth values.
3. Build and start the stack:

```bash
docker compose up --build
```

## Run Locally Without Docker
### Backend
```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `GET /github/authorize`
- `POST /github/callback?code=...`
- `POST /github/start-analysis`
- `GET /analysis/job`
- `GET /analysis/metrics`
- `GET /analysis/personality`
- `GET /analysis/history`
- `GET /reports/download`

## Sample Walkthrough
1. Register a user in the UI.
2. Login and click **Authorize GitHub**.
3. After OAuth, click **Run analysis**.
4. Watch the progress screen update.
5. View dashboard analytics and export the report.

## Tests
```bash
cd backend
pytest
```
