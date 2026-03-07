from __future__ import annotations

import io
from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PosTransaction
from app.services.dataset_context_service import get_menu_item_fallback

REQUIRED_COLUMNS = {
    "order_id",
    "transaction_date",
    "item_name",
    "category",
    "quantity",
    "unit_price",
    "food_cost_per_unit",
    "line_revenue",
    "line_contribution_margin",
}


def parse_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["item_name"] = df["item_name"].astype(str).str.strip()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
    for col in ["quantity", "unit_price", "food_cost_per_unit", "line_revenue", "line_contribution_margin"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing categorical/price fields from menu dataset context when available.
    if "category" in df.columns:
        df["category"] = df["category"].astype(str).str.strip()
    else:
        df["category"] = ""

    for idx, row in df.iterrows():
        fallback = get_menu_item_fallback(str(row["item_name"]))
        if not fallback:
            continue
        category_val = str(row.get("category", "")).strip()
        if not category_val or category_val.lower() == "nan":
            df.at[idx, "category"] = str(fallback["category"])
        if pd.isna(row.get("unit_price")):
            df.at[idx, "unit_price"] = float(fallback["selling_price"])
        if pd.isna(row.get("food_cost_per_unit")):
            df.at[idx, "food_cost_per_unit"] = float(fallback["food_cost"])

    if df[["quantity", "unit_price", "food_cost_per_unit"]].isnull().any().any():
        raise ValueError("Numeric columns contain invalid values")

    # Recompute line values when missing or invalid.
    df["line_revenue"] = df["line_revenue"].fillna(df["quantity"] * df["unit_price"])
    unit_food_cost = df["food_cost_per_unit"] * df["quantity"]
    df["line_contribution_margin"] = df["line_contribution_margin"].fillna(df["line_revenue"] - unit_food_cost)

    if "category" in df.columns:
        df["category"] = df["category"].replace({"nan": "", "NaN": ""})
        df["category"] = df["category"].replace({"": "uncategorized"})
    else:
        df["category"] = "uncategorized"

    return df


def ingest_pos_dataframe(db: Session, restaurant_id: str, df: pd.DataFrame) -> int:
    inserted = 0

    existing_keys = {
        (row.order_id, row.item_name, row.transaction_date)
        for row in db.execute(
            select(PosTransaction.order_id, PosTransaction.item_name, PosTransaction.transaction_date).where(
                PosTransaction.restaurant_id == restaurant_id
            )
        ).all()
    }

    for rec in df.to_dict(orient="records"):
        key = (str(rec["order_id"]), str(rec["item_name"]), rec["transaction_date"])
        if key in existing_keys:
            continue

        db.add(
            PosTransaction(
                restaurant_id=restaurant_id,
                order_id=str(rec["order_id"]),
                transaction_date=rec["transaction_date"],
                item_name=str(rec["item_name"]),
                category=str(rec["category"]),
                quantity=int(rec["quantity"]),
                unit_price=float(rec["unit_price"]),
                food_cost_per_unit=float(rec["food_cost_per_unit"]),
                line_revenue=float(rec["line_revenue"]),
                line_contribution_margin=float(rec["line_contribution_margin"]),
                ingested_at=datetime.now(UTC),
            )
        )
        inserted += 1

    db.commit()
    return inserted
