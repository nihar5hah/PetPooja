import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./petpooja_stage7.db"

from app.db.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402


def main() -> None:
    if os.path.exists("petpooja_stage7.db"):
        os.remove("petpooja_stage7.db")

    init_db()
    client = TestClient(app)

    with open("sample_pos.csv", "rb") as fh:
        client.post(
            "/ingestion/pos-transactions",
            params={"restaurant_id": "default_restaurant"},
            files={"file": ("sample_pos.csv", fh, "text/csv")},
        )

    client.post("/analytics/recompute", params={"restaurant_id": "default_restaurant"})

    voice_payload = {
        "restaurant_id": "default_restaurant",
        "call_id": "call-007",
        "customer_phone": "+911111111111",
        "ordered_items": [{"item_name": "Pizza", "quantity": 1}, {"item_name": "Garlic Bread", "quantity": 1}],
        "confirm_order": True,
        "transcript": "I want one pizza and one garlic bread",
        "event_type": "call_complete",
    }
    voice_res = client.post("/voice/retell-webhook", json=voice_payload)

    summary = client.get("/dashboard/summary", params={"restaurant_id": "default_restaurant"})
    menu_eng = client.get("/dashboard/menu-engineering", params={"restaurant_id": "default_restaurant"})
    combos = client.get("/dashboard/combos", params={"restaurant_id": "default_restaurant", "limit": 5})
    orders = client.get("/orders", params={"restaurant_id": "default_restaurant"})

    print("voice", voice_res.status_code, voice_res.json())
    print("summary", summary.status_code, summary.json())
    print("menu_engineering_buckets", menu_eng.status_code, menu_eng.json().get("buckets", []))
    print("combos", combos.status_code, len(combos.json()))
    print("orders", orders.status_code, len(orders.json()))


if __name__ == "__main__":
    main()
