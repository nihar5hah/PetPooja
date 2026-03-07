# PetPooja Frontend Dashboard

Next.js dashboard that visualizes orders, menu engineering, combos, and AI insights.

## Run locally

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Required backend endpoints

- `GET /dashboard/summary`
- `GET /dashboard/menu-engineering`
- `GET /dashboard/combos`
- `GET /orders`
- `GET /menu-insights`
