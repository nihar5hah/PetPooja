# PetPooja Backend (Module 1)

FastAPI backend for revenue intelligence and menu optimization.

## Endpoints

- `POST /ingestion/pos-transactions`
- `POST /analytics/recompute`
- `GET /menu-insights`
- `GET /combo-recommendations`
- `GET /upsell-suggestions`
- `GET /health`

## Local Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.init_db
uvicorn app.main:app --reload
```

## Seed Set2 Datasets

Use the menu and POS CSVs in the repository root to populate transactions and menu context,
then recompute menu metrics and combo rules:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python scripts/seed_set2_datasets.py --replace
```

## Environment

Create `.env` with:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/petpooja
LLM_PROVIDER=gemini
GEMINI_API_KEY=
LLM_MODEL=gemini-3.1-flash-lite-preview
RETELL_API_KEY=
RETELL_WEBHOOK_SECRET=
DATASET_MENU_CSV_PATH=Menu_Items_Set2.csv
DATASET_POS_CSV_PATH=POS_Transactions_Set2.csv
```
