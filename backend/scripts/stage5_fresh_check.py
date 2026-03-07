import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./petpooja_stage5.db"

from app.db.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402


def main() -> None:
    if os.path.exists("petpooja_stage5.db"):
        os.remove("petpooja_stage5.db")

    init_db()
    client = TestClient(app)

    with open("sample_pos.csv", "rb") as fh:
        r1 = client.post(
            "/ingestion/pos-transactions",
            params={"restaurant_id": "default_restaurant"},
            files={"file": ("sample_pos.csv", fh, "text/csv")},
        )

    with open("sample_pos.csv", "rb") as fh:
        r2 = client.post(
            "/ingestion/pos-transactions",
            params={"restaurant_id": "default_restaurant"},
            files={"file": ("sample_pos.csv", fh, "text/csv")},
        )

    r3 = client.post("/analytics/recompute", params={"restaurant_id": "default_restaurant"})
    r4 = client.get("/menu-insights", params={"restaurant_id": "default_restaurant"})
    r5 = client.get(
        "/combo-recommendations",
        params={"restaurant_id": "default_restaurant", "item_name": "Pizza"},
    )
    r6 = client.get(
        "/upsell-suggestions",
        params={"restaurant_id": "default_restaurant", "item_name": "Pizza"},
    )

    print("first_ingest", r1.status_code, r1.json())
    print("second_ingest", r2.status_code, r2.json())
    print("recompute", r3.status_code, r3.json())
    print("menu_insights_count", r4.status_code, len(r4.json()))
    print("combo_count", r5.status_code, len(r5.json()))
    print("upsell_count", r6.status_code, len(r6.json()))


if __name__ == "__main__":
    main()
