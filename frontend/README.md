# Ranchi Synapsters Frontend

Dark, glassy cybercrime command center UI for the Ranchi Synapsters intelligence API.

## Quick start

```bash
cd frontend
cp .env.example .env   # adjust API URL if needed
npm install            # or pnpm i / yarn
npm run dev            # starts on http://localhost:5173

# or one-liner
./starter.sh
```

## What it shows

- Live network graph (Cytoscape) from `/api/v1/intelligence/graph`
- Graph statistics from `/api/v1/system/graph/stats`
- Kingpins from `/api/v1/intelligence/kingpins`
- Fraud rings from `/api/v1/intelligence/clusters`
- Timeline, anomalies, risk for any entity via `/api/v1/intelligence/*`
- CSV uploads to `/api/v1/data/upload`

Set `VITE_API_BASE` in `.env` if your API host/port differs.
