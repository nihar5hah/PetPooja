from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import MenuMetric, PosTransaction


def classify_menu_item(avg_margin: float, popularity_score: float, margin_threshold: float, popularity_threshold: float) -> str:
    if avg_margin >= margin_threshold and popularity_score >= popularity_threshold:
        return "STAR"
    if avg_margin >= margin_threshold and popularity_score < popularity_threshold:
        return "PUZZLE"
    if avg_margin < margin_threshold and popularity_score >= popularity_threshold:
        return "CASH_COW"
    return "DOG"


def build_menu_metrics_df(transactions_df: pd.DataFrame) -> pd.DataFrame:
    if transactions_df.empty:
        return pd.DataFrame()

    grouped = (
        transactions_df.groupby("item_name", as_index=False)
        .agg(
            total_sales_qty=("quantity", "sum"),
            total_revenue=("line_revenue", "sum"),
            avg_margin=("line_contribution_margin", "mean"),
            first_date=("transaction_date", "min"),
            last_date=("transaction_date", "max"),
        )
        .copy()
    )

    span_days = (grouped["last_date"] - grouped["first_date"]).dt.days.clip(lower=0) + 1
    grouped["sales_velocity"] = grouped["total_sales_qty"] / span_days

    total_qty = grouped["total_sales_qty"].sum()
    grouped["popularity_score"] = grouped["total_sales_qty"] / total_qty if total_qty else 0
    grouped["margin_score"] = grouped["avg_margin"]

    margin_threshold = grouped["avg_margin"].median()
    popularity_threshold = grouped["popularity_score"].median()

    grouped["menu_class"] = grouped.apply(
        lambda row: classify_menu_item(
            avg_margin=float(row["avg_margin"]),
            popularity_score=float(row["popularity_score"]),
            margin_threshold=float(margin_threshold),
            popularity_threshold=float(popularity_threshold),
        ),
        axis=1,
    )

    grouped.drop(columns=["first_date", "last_date"], inplace=True)
    return grouped


def get_underperformers(metrics_df: pd.DataFrame) -> pd.DataFrame:
    if metrics_df.empty:
        return metrics_df
    return metrics_df[metrics_df["menu_class"] == "PUZZLE"].sort_values("avg_margin", ascending=False)


def recompute_menu_metrics(db: Session, restaurant_id: str) -> tuple[int, datetime]:
    rows = db.execute(
        select(PosTransaction).where(PosTransaction.restaurant_id == restaurant_id)
    ).scalars().all()

    if not rows:
        db.execute(delete(MenuMetric).where(MenuMetric.restaurant_id == restaurant_id))
        db.commit()
        return 0, datetime.now(UTC)

    data = []
    for row in rows:
        data.append(
            {
                "item_name": row.item_name,
                "quantity": row.quantity,
                "line_revenue": row.line_revenue,
                "line_contribution_margin": row.line_contribution_margin,
                "transaction_date": pd.to_datetime(row.transaction_date),
            }
        )

    df = pd.DataFrame(data)
    metrics_df = build_menu_metrics_df(df)

    db.execute(delete(MenuMetric).where(MenuMetric.restaurant_id == restaurant_id))
    computed_at = datetime.now(UTC)

    for rec in metrics_df.to_dict(orient="records"):
        db.add(
            MenuMetric(
                restaurant_id=restaurant_id,
                item_name=rec["item_name"],
                total_sales_qty=int(rec["total_sales_qty"]),
                total_revenue=float(rec["total_revenue"]),
                avg_margin=float(rec["avg_margin"]),
                sales_velocity=float(rec["sales_velocity"]),
                popularity_score=float(rec["popularity_score"]),
                margin_score=float(rec["margin_score"]),
                menu_class=str(rec["menu_class"]),
                computed_at=computed_at,
            )
        )

    db.commit()
    return len(metrics_df), computed_at
