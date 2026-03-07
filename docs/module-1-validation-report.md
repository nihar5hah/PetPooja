# Module 1 Validation Report

Date: 2026-03-06

## Environment

- Python: 3.13.5
- Backend dependencies installed from `backend/requirements.txt`
- Validation DB: local SQLite (`petpooja_stage5.db`)

## Validation Commands

```bash
cd backend
source .venv/bin/activate
pytest -q
PYTHONPATH=. python -u scripts/stage5_fresh_check.py
```

## Results

### Unit Tests

- `3 passed`

### Ingestion and Idempotency

- First ingestion: `rows_received=14`, `rows_inserted=14`
- Second ingestion of same CSV: `rows_received=14`, `rows_inserted=0`

### Analytics Recompute

- `items_processed=6`
- `combo_rules_generated=8`

### Required Module 1 Endpoints

- `GET /menu-insights` -> `200`, returned `6` insights
- `GET /combo-recommendations?item_name=Pizza` -> `200`, returned `2` recommendations
- `GET /upsell-suggestions?item_name=Pizza` -> `200`, returned `2` suggestions

### Sample Output Evidence

- Top insight item: `Pizza` classified as `STAR`
- Combo sample: `Pizza -> Coke` with confidence `0.6`
- Upsell sample for Pizza includes `Coke` and `Garlic Bread`

## Stage 5 Verdict

Module 1 validation criteria passed for:

- ingestion
- aggregation and menu classification
- combo recommendations
- upsell suggestions
- menu insight generation

Module 1 is validated and ready for Module 2 development.
