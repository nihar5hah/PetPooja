# PetPooja Hackathon Final Submission

## 1. Executive Summary

PetPooja is an AI restaurant ordering and revenue intelligence system built to connect customer ordering, upsell intelligence, order persistence, and live business visibility in one workflow. Instead of treating voice ordering and restaurant analytics as separate products, PetPooja combines them: a voice agent can validate menu items, recommend profitable combos from historical POS data, create the order, and immediately push the business impact to a live dashboard.

The project is implemented with a FastAPI backend, a Next.js dashboard, Supabase PostgreSQL for persistence and realtime updates, Retell for voice interactions, and ngrok for development-time public exposure. The intelligence layer is grounded in two datasets included in the repository: `Menu_Items_Set2.csv` for menu context and `POS_Transactions_Set2.csv` for transaction-driven analytics.

For the hackathon, the system demonstrates a complete loop:

1. A customer order begins through a voice interaction.
2. The backend validates the requested item against the menu dataset.
3. PetPooja surfaces combo recommendations based on association rules mined from POS history.
4. A confirmed order is created and persisted.
5. Analytics are recomputed and the dashboard refreshes through Supabase Realtime.

This turns every successful order into both a transaction and a new analytics signal.

## 2. Problem Statement

Restaurants lose revenue in three common places:

1. Manual or inconsistent order taking creates menu mismatches, missed items, and slow confirmations.
2. Upsell decisions are often intuition-based rather than backed by actual purchase patterns.
3. Business dashboards lag behind operations, so operators cannot see the immediate effect of newly placed orders.

These issues are amplified in voice-ordering scenarios. Spoken menu items may be misheard, agent flows can become brittle, and even when an order is successfully captured, the order data often does not flow back into the restaurant's revenue intelligence layer in real time.

PetPooja addresses that gap by combining voice-safe ordering APIs with transaction-backed recommendation logic and a dashboard that reflects confirmed orders as soon as they land in the database.

## 3. Solution Overview

PetPooja is designed as a connected system with four layers:

1. **Conversation layer**: Retell voice agent handles the customer interaction.
2. **Application layer**: FastAPI exposes APIs for menu retrieval, item validation, combo recommendations, order creation, analytics recomputation, dashboard views, and voice webhooks.
3. **Data and intelligence layer**: Supabase PostgreSQL stores transactional and analytics tables, while pandas and mlxtend drive metric computation and combo mining.
4. **Presentation layer**: Next.js dashboard visualizes orders, KPIs, menu engineering, combo performance, and insights with realtime refresh.

The core product idea is simple: use historical restaurant data to make the AI ordering flow smarter, then feed live orders back into the same system so operations and analytics stay aligned.

## 4. Architecture

### High-level architecture

```text
Customer Call
    |
    v
Retell Voice Agent
    |
    | function calls / webhook
    v
FastAPI Backend
    |-- /menu
    |-- /validate-item
    |-- /combo-recommendations
    |-- /create-order
    |-- /voice/retell-webhook
    |-- /dashboard/*
    |-- /extended-analytics/*
    v
Supabase PostgreSQL
    |-- orders
    |-- order_items
    |-- pos_transactions
    |-- menu_metrics
    |-- combo_rules
    |-- voice_call_logs
    |-- failed_order_queue
    v
Next.js Dashboard
    |
    v
Realtime KPI + order + combo updates
```

### Repository architecture

- `backend/`: FastAPI application, services, schemas, scripts, and tests.
- `frontend/`: Next.js dashboard application.
- `infra/sql/`: base schema and Supabase Realtime publication SQL.
- `docs/`: runbook, demo flow, and staged validation reports.
- Root CSV files: `Menu_Items_Set2.csv` and `POS_Transactions_Set2.csv`.

### Architecture notes

- The backend initializes the database on app startup.
- CORS is enabled for local frontend hosts and ngrok subdomains.
- Supabase Realtime is configured on `orders`, `pos_transactions`, `menu_metrics`, `combo_rules`, and `failed_order_queue`.
- The frontend subscribes to database changes and triggers a debounced refresh cycle.

## 5. Core Features

### 5.1 Menu validation

The system validates spoken items against the menu dataset before adding them to an order. This reduces incorrect order capture and gives the voice agent a deterministic menu guardrail.

Implemented behavior:

- `POST /validate-item`
- Loads active menu candidates from the menu CSV context
- Resolves item names using menu aliases and fuzzy matching
- Returns valid match or suggested name when confidence is lower

### 5.2 Combo recommendations

PetPooja recommends relevant add-ons and combos using association rules mined from POS transactions. This is not a static combo list; it is generated from transaction behavior.

Implemented behavior:

- `GET /combo-recommendations`
- Supports `format=simple` for voice-agent-safe recommendations
- Ranks suggestions using rule quality signals such as confidence, lift, and combo score

### 5.3 Create-order integration

Once the user confirms the cart, the backend creates the order, writes order items, and inserts analytics-compatible rows into `pos_transactions` so the order becomes part of the reporting layer immediately.

Implemented behavior:

- `POST /create-order`
- Resolves and revalidates all requested items before persistence
- Creates an external order ID
- Persists `orders` and `order_items`
- Inserts mirrored rows into `pos_transactions`

### 5.4 Analytics recompute

After a confirmed order is created, the backend attempts to recompute menu metrics and combo rules so the intelligence layer stays current with the latest transactional data.

Implemented behavior:

- `POST /analytics/recompute`
- Order creation path also invokes recompute routines
- Rebuilds menu engineering metrics and combo rules

### 5.5 Dashboard realtime refresh

The Next.js dashboard listens for Supabase Postgres change events and refreshes summary, menu engineering, combo, insights, and order views when relevant tables change.

Implemented behavior:

- Subscribes to `orders`, `pos_transactions`, `menu_metrics`, and `combo_rules`
- Uses a debounce window to avoid excessive refresh churn
- Updates KPI cards, recent orders, combos, category revenue, and menu insights

### 5.6 Voice workflow support and failure handling

The project includes a Retell webhook path, voice call logging, and a failed order queue with retry support for resilience in development and demo scenarios.

Implemented behavior:

- `POST /voice/retell-webhook`
- Signature verification for Retell webhook requests
- `GET /orders`
- `POST /failed-orders/{queue_id}/retry`

## 6. End-to-End Workflow

### Primary happy path

1. A customer begins a call with the Retell voice agent.
2. The agent uses `POST /validate-item` to confirm a spoken item exists in the menu dataset.
3. The agent calls `GET /combo-recommendations?format=simple&item_name=...` to fetch relevant upsell suggestions.
4. The customer confirms the final cart.
5. The agent calls `POST /create-order` with the approved items.
6. The backend stores the order in `orders` and `order_items`.
7. The backend also inserts line-level transaction rows into `pos_transactions`.
8. Menu metrics and combo rules are recomputed.
9. Supabase Realtime publishes table changes.
10. The Next.js dashboard refreshes and shows the new order, updated revenue, and updated intelligence views.

### Voice webhook simulation path

The repository also supports a webhook-driven development flow where `POST /voice/retell-webhook` processes pending and confirmed order states. The validation script demonstrates:

- a pending confirmation response for an uncertain or unconfirmed voice order
- a confirmed response after customer approval
- the resulting order becoming visible through `GET /orders`

## 7. Technical Implementation Details

### Backend

- Framework: FastAPI 0.115
- ORM/data access: SQLAlchemy 2.0
- Database driver: psycopg 3
- Data processing: pandas 2.2
- Association rule mining: mlxtend 0.23
- Validation/models: Pydantic 2

Key implementation details:

- The application bootstraps the database during FastAPI lifespan startup.
- CORS is configured for localhost frontend development and ngrok public URLs.
- Order creation normalizes items using menu fallback context before persistence.
- Order persistence records both business-facing entities (`orders`, `order_items`) and analytics-facing transaction rows (`pos_transactions`).
- Analytics recompute runs immediately after integration order creation.

### Intelligence pipeline

- `Menu_Items_Set2.csv` provides item-level attributes such as item name, price, category, and food cost context.
- `POS_Transactions_Set2.csv` drives menu performance and association-rule generation.
- Menu engineering output classifies items into buckets such as `STAR`, `PUZZLE`, `CASH_COW`, and `DOG`.
- Combo recommendations are filtered and ranked using support, confidence, lift, and rule strength.

### Frontend

- Framework: Next.js 14.2 with React 18
- Visualization: Recharts
- Motion/UI polish: Framer Motion, Lucide icons, Tailwind CSS 4
- Data refresh: Supabase client subscriptions plus frontend fetch refresh

Dashboard implementation highlights:

- Server-side initial data load for summary, menu engineering, combos, insights, orders, KPIs, and category metrics
- Client-side realtime refresh hook that subscribes to Postgres change events
- Visual coverage for KPI cards, recent orders, top combos, category revenue, and menu insights

## 8. APIs and Integrations

### Core integration APIs

| Endpoint | Method | Purpose |
|---|---|---|
| `/menu` | `GET` | Return active menu items for voice-safe menu access |
| `/validate-item` | `POST` | Validate or suggest a menu item from customer speech |
| `/combo-recommendations` | `GET` | Return detailed or simplified combo recommendations |
| `/create-order` | `POST` | Persist a confirmed order and sync analytics data |

### Voice and order operations

| Endpoint | Method | Purpose |
|---|---|---|
| `/voice/retell-webhook` | `POST` | Accept Retell webhook events for voice ordering flow |
| `/orders` | `GET` | View recent confirmed orders |
| `/failed-orders/{queue_id}/retry` | `POST` | Retry failed order persistence |

### Dashboard APIs

| Endpoint | Method | Purpose |
|---|---|---|
| `/dashboard/summary` | `GET` | Revenue, order count, AOV, and top selling summary |
| `/dashboard/menu-engineering` | `GET` | Bucketed menu engineering results |
| `/dashboard/combos` | `GET` | Top combo rules for dashboard display |
| `/dashboard/menu-items` | `GET` | Filterable item details |
| `/dashboard/voice-logs` | `GET` | Voice interaction log visibility |
| `/dashboard/failed-orders` | `GET` | Failed queue visibility |

### Extended analytics APIs

The project also exposes a broader analytics surface under `/extended-analytics`, including:

- restaurant KPIs
- order metrics
- item metrics
- category metrics
- popularity vs. profitability views
- basket metrics
- combo performance
- upsell signals
- price optimization
- strategy cards for hidden gems and watch list views

### External integrations

- **Supabase PostgreSQL**: primary database plus realtime eventing.
- **Retell AI**: voice agent interaction and webhook flow.
- **ngrok**: development-time HTTPS exposure for external webhook/function access.

The repository includes a ready reference for Retell function calling in `docs/retell_functions.json` with function definitions for menu validation, combo lookup, and order finalization.

## 9. Database / Data Model Summary

PetPooja uses a pragmatic hybrid model: transactional tables for live orders, analytics tables for derived intelligence, and support tables for voice operations.

### Transactional and operational tables

| Table | Purpose |
|---|---|
| `orders` | confirmed order header records |
| `order_items` | line items for each order |
| `voice_call_logs` | transcript and webhook payload traceability |
| `failed_order_queue` | failed persistence queue with retry state |

### Analytics tables

| Table | Purpose |
|---|---|
| `pos_transactions` | line-level transaction facts used for analytics |
| `menu_metrics` | computed menu engineering metrics |
| `combo_rules` | mined item association rules |

### Support tables

| Table | Purpose |
|---|---|
| `menu_aliases` | alias-to-canonical item mapping for spoken item resolution |

### Data model design choice

The important design decision is that a confirmed voice order is not stored only as an order header. It is also converted into transaction rows in `pos_transactions`, allowing the same event to affect both operational views and analytics views without a separate ETL job.

## 10. Setup and Run Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Access to a PostgreSQL or Supabase database
- Optional keys for Retell and Gemini-backed features if used in the environment
- ngrok installed for public dev exposure

### Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python -m app.db.init_db
uvicorn app.main:app --reload
```

### Seed analytics datasets

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python scripts/seed_set2_datasets.py --replace
```

### Frontend setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Enable Supabase Realtime

Run the SQL in `infra/sql/002_enable_dashboard_realtime.sql` to publish relevant tables.

### Start ngrok for Retell development

```bash
./scripts/start_ngrok.sh 8000
```

Use the generated HTTPS URL in `docs/retell_functions.json` or Retell configuration during development.

## 11. Demo Script / Judging Flow

### Demo objective

Show that PetPooja does more than take an order. It converts a voice interaction into a validated, upsell-aware, analytics-connected restaurant workflow.

### Recommended judging flow

1. Start the backend and frontend.
2. Seed the datasets.
3. Open the dashboard.
4. Explain that combo intelligence comes from historical POS data, not hardcoded upsells.
5. Trigger a voice-order simulation for `Paneer Pizza`.
6. Show the pending state for the initial voice flow if using webhook simulation.
7. Confirm the order with an accepted upsell such as `Garlic Bread`.
8. Show the successful order creation response with an assigned order ID.
9. Move to the dashboard and show:
   - recent order presence
   - revenue and AOV update
   - combo rule visibility
   - menu intelligence or recommendation context
10. Close by explaining that the newly created order is also inserted into the analytics fact table and triggers realtime UI refresh.

### Key judging talking points

- Voice ordering is connected to real restaurant data.
- Item validation reduces order capture errors.
- Upsells are data-backed rather than manually scripted.
- Analytics update after a live order, not only in batch.
- The dashboard provides operator visibility immediately after confirmation.

## 12. Validation / Testing Evidence

The project includes staged verification artifacts and runnable validation scripts in the repository.

### Evidence from existing docs

- **Stage 7 Integration Report** confirms unified dashboard APIs, voice-order integration with analytics, and end-to-end validation.
- **Stage 8 Final Verification Report** states the project is demo-ready with backend checks, voice simulation, integration simulation, and frontend build readiness.
- **Runbook** documents the full operational startup and validation sequence.
- **Demo Script** documents the recommended live walkthrough.

### Automated and scripted validation

Commands documented in the repo:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest -q
PYTHONPATH=. python -m compileall app
PYTHONPATH=. python -u scripts/stage5_fresh_check.py
PYTHONPATH=. python -u scripts/stage6_voice_validation.py
PYTHONPATH=. python -u scripts/stage7_integration_validation.py
```

```bash
cd frontend
npm install
npm run build
```

### Reported verification outcomes

- Stage 7 recorded `pytest -q -> 6 passed`.
- Backend compile checks succeeded.
- Voice simulation demonstrated pending and confirmed paths.
- Confirmed voice orders became queryable through the orders API.
- Dashboard summary, menu engineering, and combo APIs returned expected outputs.
- Frontend was validated for build readiness in Stage 8.

## 13. Challenges and Tradeoffs

### 13.1 Realtime intelligence vs. synchronous simplicity

The current implementation recomputes analytics immediately after order creation. This keeps the demo simple and makes the live effect visible, but it also means analytics work happens in the request path rather than through an async job queue.

### 13.2 Development exposure vs. production deployment

ngrok is a practical solution for hackathon development and Retell connectivity, but it introduces ephemeral URLs and a manual configuration step for external integrations.

### 13.3 Fuzzy validation accuracy vs. strict correctness

Voice ordering benefits from fuzzy matching and alias resolution, but the system still needs confidence thresholds to avoid incorrect item substitutions. PetPooja uses a thresholded approach to balance flexibility and safety.

### 13.4 Unified analytics writeback vs. data purity

Writing confirmed orders directly into both order tables and `pos_transactions` makes the product responsive and demo-friendly. The tradeoff is that analytics ingestion and operational writes are coupled in the same workflow.

### 13.5 Single-restaurant default vs. multi-tenant scope

The current repo is structured around a default restaurant workflow, which is appropriate for a focused hackathon prototype. A production deployment would need stronger tenancy boundaries, auth, and configuration management.

## 14. Future Improvements

1. Move analytics recompute to background jobs for lower write latency and better scale.
2. Add production-grade authentication and role-based dashboard access.
3. Support multi-restaurant isolation with tenant-aware configuration and data boundaries.
4. Add richer agent-side cart memory and conversation state recovery.
5. Persist and visualize full voice session histories for QA and coaching.
6. Expand retry and dead-letter handling for failed orders.
7. Add deployment automation for backend, frontend, and Supabase schema setup.
8. Add benchmark metrics around upsell conversion, validation accuracy, and refresh latency.
9. Replace ngrok-based development exposure with stable production endpoints.
10. Add stronger observability, tracing, and alerting around voice and order workflows.

## 15. Repository and Submission Links

- Repository: https://github.com/nihar5hah/PetPooja
- Demo video: _TBD_
- Deployed frontend: _TBD_
- Deployed backend / public API base URL: _TBD_
- Pitch deck: _TBD_
- Submission form / hackathon portal link: _TBD_

## Closing Summary

PetPooja demonstrates a practical AI restaurant workflow where voice ordering, menu validation, upsell intelligence, order persistence, and realtime dashboard visibility work together. The value of the project is not just in any single endpoint or chart, but in the fact that each confirmed order becomes both an operational event and an analytics event. That integration is the core product story for the final submission.