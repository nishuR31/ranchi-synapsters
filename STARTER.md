# Quick Start

## Backend (FastAPI + Neo4j)

```bash
cd app
python -m venv venv
# activate venv
venv\Scripts\activate    # Windows
# or
source venv/bin/activate   # macOS/Linux

# install deps (prefer Python 3.10/3.11 for wheels)
python -m pip install --upgrade pip
pip install -r requirements.txt

# run API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- Ensure Neo4j is running and `.env` (if present) has correct credentials.
- Health check: `curl http://localhost:8000/api/v1/system/health`

## Frontend (React + Tailwind v4)

```bash
cd frontend
npm install
npm run dev   # opens http://localhost:5173
```

Configure API base (if not default): set `VITE_API_BASE` in `frontend/.env`.
