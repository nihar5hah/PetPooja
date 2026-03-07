# Module 1 Validation Checklist

## Data Ingestion

- Upload valid CSV with required columns to `POST /ingestion/pos-transactions`
- Re-upload same CSV and verify `rows_inserted` does not increase for duplicate records

## Analytics Computation

- Trigger `POST /analytics/recompute`
- Verify records appear in `menu_metrics`
- Confirm menu classes include expected values (`STAR`, `PUZZLE`, `CASH_COW`, `DOG`)

## Combo and Upsell

- Call `GET /combo-recommendations` and verify non-empty rules for common items
- Call `GET /upsell-suggestions?item_name=Pizza`
- Verify suggestions include confidence and expected margin uplift fields

## Insights

- Call `GET /menu-insights`
- Validate each response contains recommendation text tied to menu class

## Acceptance Gate

Module 1 is complete when all checklist items pass and API outputs match fixture expectations.
