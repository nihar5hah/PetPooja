import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure settings pick up SQLite for local validation.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./petpooja_stage5.db"

from app.db.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402


def run() -> dict:
    init_db()
    client = TestClient(app)

    csv_path = Path(__file__).resolve().parent.parent / "sample_pos.csv"
    with csv_path.open("rb") as fh:
        ingestion_res = client.post(
            "/ingestion/pos-transactions",
            params={"restaurant_id": "default_restaurant"},
            files={"file": ("sample_pos.csv", fh, "text/csv")},
        )

    recompute_res = client.post("/analytics/recompute", params={"restaurant_id": "default_restaurant"})
    menu_insights_res = client.get("/menu-insights", params={"restaurant_id": "default_restaurant"})
    combo_res = client.get(
        "/combo-recommendations",
        params={"restaurant_id": "default_restaurant", "item_name": "Pizza"},
    )
    upsell_res = client.get(
        "/upsell-suggestions",
        params={"restaurant_id": "default_restaurant", "item_name": "Pizza"},
    )

    payload = {
        "ingestion": ingestion_res.json(),
        "recompute": recompute_res.json(),
        "menu_insights_count": len(menu_insights_res.json()),
        "top_menu_insight": menu_insights_res.json()[0] if menu_insights_res.json() else None,
        "combo_sample": combo_res.json()[:3],
        "upsell_sample": upsell_res.json()[:3],
        "status_codes": {
            "ingestion": ingestion_res.status_code,
            "recompute": recompute_res.status_code,
            "menu_insights": menu_insights_res.status_code,
            "combo": combo_res.status_code,
            "upsell": upsell_res.status_code,
        },
    }
    return payload


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
