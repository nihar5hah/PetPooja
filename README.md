# PetPooja

PetPooja is an AI-assisted restaurant ordering and revenue intelligence system built around five connected pieces:

- a FastAPI backend
- a Next.js dashboard
- a Supabase PostgreSQL database
- analytics datasets for menu items and POS transactions
- a Retell voice agent exposed through ngrok during development

The system supports an end-to-end flow where a caller places an order through the voice agent, the backend validates menu items against the dataset, suggests combo recommendations from analytics, creates the order in the database, inserts transaction rows for analytics, and updates the dashboard through Supabase Realtime.

## Features

- Voice-agent-safe public APIs for menu fetch, item validation, combo lookup, and order finalization
- Dataset-driven menu validation using `Menu_Items_Set2.csv`
- Analytics-driven combo recommendations using mined association rules from `POS_Transactions_Set2.csv`
- Automatic insertion of voice orders into transactional analytics tables
- Supabase-backed dashboard with revenue, menu engineering, combos, pricing, hidden gems, and watch-list views
- Retell integration support through function calling and ngrok
- Realtime dashboard refresh using Supabase subscriptions

## Architecture

### Backend

The backend lives in [backend](./backend) and is built with FastAPI, SQLAlchemy, PostgreSQL, pandas, and mlxtend.

Core responsibilities:

- ingest and seed analytics datasets
- compute menu metrics and combo rules
- expose dashboard APIs
- process voice-agent order flows
- persist orders and sync them into `pos_transactions`

Key public integration endpoints:

- `GET /menu`
- `POST /validate-item`
- `GET /combo-recommendations?format=simple&item_name=...`
- `POST /create-order`

### Frontend

The frontend lives in [frontend](./frontend) and is built with Next.js 14, React 18, Tailwind CSS, Framer Motion, and Recharts.

Main views:

- dashboard overview
- menu intelligence hub
- orders and failed queue
- combos and upsell views
- operations and CSV ingestion
- voice lab simulator

### Data Layer

Primary datasets:

- [Menu_Items_Set2.csv](./Menu_Items_Set2.csv)
- [POS_Transactions_Set2.csv](./POS_Transactions_Set2.csv)

Database schema and realtime SQL:

- [infra/sql/001_init_schema.sql](./infra/sql/001_init_schema.sql)
- [infra/sql/002_enable_dashboard_realtime.sql](./infra/sql/002_enable_dashboard_realtime.sql)

## Repository Structure

```text
PetPooja/
├── backend/                    FastAPI backend
├── frontend/                   Next.js dashboard
├── docs/                       validation reports, runbooks, demo notes
├── infra/sql/                  schema and realtime SQL
├── scripts/                    utility scripts such as ngrok startup
├── Menu_Items_Set2.csv         menu dataset
└── POS_Transactions_Set2.csv   POS transaction dataset
```

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python -m app.db.init_db
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### 3. Seed the Datasets

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python scripts/seed_set2_datasets.py --replace
```

### 4. Enable Supabase Realtime

Run the SQL in [infra/sql/002_enable_dashboard_realtime.sql](./infra/sql/002_enable_dashboard_realtime.sql).

### 5. Start ngrok for Retell Development

```bash
./scripts/start_ngrok.sh 8000
```

Use the generated HTTPS URL in the Retell function configuration file at [docs/retell_functions.json](./docs/retell_functions.json).

## Retell Integration Flow

1. Customer calls the Retell voice agent
2. The agent validates requested items through `/validate-item`
3. The agent fetches upsell opportunities through `/combo-recommendations`
4. The agent confirms the full order
5. The backend stores the order in `orders` and `order_items`
6. The backend also writes rows into `pos_transactions`
7. Analytics recompute and the dashboard refreshes through Supabase Realtime

## Important Notes

- Do not commit real `.env` files or local virtual environments
- Do not include `node_modules`, `.next`, `.venv`, or local database files in submission archives
- The repo includes example docs and validation reports in [docs](./docs)

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL / Supabase
- pandas
- mlxtend
- Next.js
- React
- Tailwind CSS
- Recharts
- Framer Motion
- Retell AI
- ngrok

## Supporting Docs

- [docs/runbook.md](./docs/runbook.md)
- [docs/demo-script.md](./docs/demo-script.md)
- [docs/stage8-final-verification-report.md](./docs/stage8-final-verification-report.md)
