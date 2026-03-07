import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./petpooja_stage6.db"

from app.db.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402


def seed_module1_data(client: TestClient) -> None:
    with open("sample_pos.csv", "rb") as fh:
        client.post(
            "/ingestion/pos-transactions",
            params={"restaurant_id": "default_restaurant"},
            files={"file": ("sample_pos.csv", fh, "text/csv")},
        )
    client.post("/analytics/recompute", params={"restaurant_id": "default_restaurant"})


def main() -> None:
    if os.path.exists("petpooja_stage6.db"):
        os.remove("petpooja_stage6.db")

    init_db()
    client = TestClient(app)

    seed_module1_data(client)

    pending_payload = {
        "restaurant_id": "default_restaurant",
        "call_id": "call-001",
        "customer_phone": "+911234567890",
        "ordered_items": [{"item_name": "paneer pizaa", "quantity": 1}],
        "confirm_order": False,
        "transcript": "I want one paneer pizaa",
        "event_type": "call_update",
    }

    confirm_payload = {
        "restaurant_id": "default_restaurant",
        "call_id": "call-001",
        "customer_phone": "+911234567890",
        "ordered_items": [{"item_name": "Paneer Pizza", "quantity": 1}, {"item_name": "Garlic Bread", "quantity": 1}],
        "confirm_order": True,
        "transcript": "Yes confirm my order",
        "event_type": "call_complete",
    }

    r1 = client.post("/voice/retell-webhook", json=pending_payload)
    r2 = client.post("/voice/retell-webhook", json=confirm_payload)
    r3 = client.get("/orders", params={"restaurant_id": "default_restaurant"})

    print("pending", r1.status_code, r1.json())
    print("confirmed", r2.status_code, r2.json())
    print("orders", r3.status_code, len(r3.json()))
    if r3.json():
        print("latest_order", r3.json()[0])


if __name__ == "__main__":
    main()
