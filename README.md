# PetPooja — Voice AI Ordering + Revenue Intelligence

> Built at a hackathon. A full-stack restaurant system where customers place orders by voice and owners get real-time revenue intelligence — all in one platform.

---

## What It Does

A customer calls a Retell-powered voice agent, tells it what they want, and the system:

1. **Validates** the order against a real menu using fuzzy matching
2. **Suggests combos** based on association rules mined from thousands of POS transactions
3. **Finalises the order** — persists it to the database and immediately feeds it into analytics
4. **Updates the dashboard** in real time via Supabase Realtime subscriptions

On the owner side, a Next.js dashboard surfaces revenue breakdowns, menu engineering quadrants (Stars / Cash Cows / Puzzles / Dogs), combo performance, upsell signals, pricing gaps, and a live order feed — all powered by the same data pipeline.

---

## Highlights

- **End-to-end voice ordering** — Retell AI agent calls three HTTP functions (validate, recommend, create) to complete a full order with natural conversation
- **Association rule mining** — mlxtend Apriori over real POS data to surface high-confidence item combos and upsell opportunities
- **Menu engineering** — BCG-style quadrant analysis with margin and popularity scores, updated on every new order
- **Supabase Realtime** — dashboard cards refresh automatically without polling the moment an order comes in
- **Fuzzy item resolution** — orders are matched to the canonical menu even when the customer names items informally

---

## Tech Stack

| Layer | Technology |
|---|---|
| Voice agent | Retell AI |
| Backend API | FastAPI, SQLAlchemy, psycopg3 |
| Analytics | pandas, mlxtend |
| Database | Supabase (PostgreSQL + Realtime) |
| Frontend | Next.js 14, React 18, Tailwind CSS, Recharts, Framer Motion |
| Tunnel (dev) | ngrok |

---

## Architecture

```
Retell Voice Agent
      │
      ├─ POST /validate-item         ← fuzzy-match item name against menu dataset
      ├─ GET  /combo-recommendations ← top association-rule pairings for the item
      └─ POST /create-order          ← persist order + trigger analytics update
                                              │
                                     Supabase PostgreSQL
                                              │
                                     Supabase Realtime ──► Next.js Dashboard
```

---

## Local Setup

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your Supabase credentials
PYTHONPATH=. python -m app.db.init_db
PYTHONPATH=. python scripts/seed_set2_datasets.py --replace
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
cp .env.example .env.local    # set NEXT_PUBLIC_API_BASE_URL
npm install && npm run dev
```

**Retell (dev)**
```bash
./scripts/start_ngrok.sh 8000
# paste the generated HTTPS URL into docs/retell_functions.json
# and configure the three functions in the Retell dashboard
```

---

## Repository Structure

```
PetPooja/
├── backend/          FastAPI + analytics engine
├── frontend/         Next.js dashboard
├── docs/             Retell function config, hackathon submission, demo script
├── infra/sql/        Schema and Supabase Realtime setup
└── scripts/          Seeding + ngrok helpers
```
