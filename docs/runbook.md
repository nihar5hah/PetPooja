# PetPooja Runbook

## 1) Backend startup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python -m app.db.init_db
uvicorn app.main:app --reload
```

## 2) Seed and validate analytics

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -u scripts/seed_set2_datasets.py --replace
PYTHONPATH=. python -u scripts/stage5_fresh_check.py
```

## 3) Validate voice flow

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -u scripts/stage6_voice_validation.py
```

## 4) Validate full integration

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -u scripts/stage7_integration_validation.py
```

## 5) Frontend startup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## 6) Final acceptance checklist

- Module 1 APIs return analytics and recommendation outputs.
- Voice webhook supports pending confirmation and confirmed order paths.
- Confirmed orders are visible in `/orders` and dashboard summary.
- Menu engineering and combo panels match backend analytics.
- Demo flow can be executed without manual DB edits.
