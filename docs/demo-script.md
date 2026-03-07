# PetPooja Demo Script (Final)

## Goal

Show how AI-driven revenue intelligence powers live voice ordering upsells and real-time dashboard visibility.

## Pre-demo setup

1. Start backend API.
2. Seed both datasets with `PYTHONPATH=. python scripts/seed_set2_datasets.py --replace`.
3. Start frontend dashboard.
4. Open dashboard at `http://localhost:3000`.

## Live flow

1. Narrate: "A customer is calling to place an order."
2. Trigger voice webhook with payload for `Paneer Pizza`.
3. Show response in pending confirmation state.
4. Trigger confirmation webhook with `confirm_order=true` and accepted upsell `Garlic Bread`.
5. Show order confirmation response (`order_id` assigned).
6. Refresh dashboard.

## Dashboard talking points

- Orders panel updates with newly confirmed voice order.
- Top combos panel highlights data-backed pairings.
- Menu engineering chart explains item classes (Star, Puzzle, Cash Cow, Dog).
- Insights panel explains why Garlic Bread is a good promotion candidate.
- AOV and revenue update as order is persisted.

## Optional resilience demo

1. Simulate failed persistence path (dev-only monkeypatch).
2. Show payload in `failed_order_queue`.
3. Retry with `POST /failed-orders/{id}/retry`.
4. Confirm queue status changes to resolved.
