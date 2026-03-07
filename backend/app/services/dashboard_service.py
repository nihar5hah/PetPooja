from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ComboRule, FailedOrderQueue, MenuMetric, Order, OrderItem, VoiceCallLog


def get_dashboard_summary(db: Session, restaurant_id: str, top_n: int = 5) -> dict:
    order_count = db.execute(
        select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)
    ).scalar_one()

    total_revenue_raw = db.execute(
        select(func.coalesce(func.sum(Order.total_amount), 0.0)).where(Order.restaurant_id == restaurant_id)
    ).scalar_one()
    total_revenue = float(total_revenue_raw or 0.0)

    avg_order_value = total_revenue / order_count if order_count else 0.0

    top_rows = db.execute(
        select(OrderItem.item_name, func.sum(OrderItem.quantity).label("qty"))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.restaurant_id == restaurant_id)
        .group_by(OrderItem.item_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(top_n)
    ).all()

    top_items = [{"item_name": row.item_name, "quantity": int(row.qty)} for row in top_rows]

    return {
        "order_count": int(order_count or 0),
        "total_revenue": total_revenue,
        "avg_order_value": float(avg_order_value),
        "top_selling_items": top_items,
    }


def get_menu_engineering(db: Session, restaurant_id: str) -> dict:
    metrics = db.execute(
        select(MenuMetric)
        .where(MenuMetric.restaurant_id == restaurant_id)
        .order_by(MenuMetric.total_revenue.desc())
    ).scalars().all()

    bucket_counts: dict[str, int] = {}
    items = []
    for metric in metrics:
        bucket_counts[metric.menu_class] = bucket_counts.get(metric.menu_class, 0) + 1
        items.append(
            {
                "item_name": metric.item_name,
                "menu_class": metric.menu_class,
                "total_revenue": float(metric.total_revenue),
                "total_sales_qty": int(metric.total_sales_qty),
            }
        )

    buckets = [{"menu_class": key, "item_count": value} for key, value in sorted(bucket_counts.items())]
    return {"buckets": buckets, "items": items}


def get_dashboard_combos(db: Session, restaurant_id: str, limit: int = 20) -> list[dict]:
    rows = db.execute(
        select(ComboRule)
        .where(ComboRule.restaurant_id == restaurant_id)
        .order_by(ComboRule.confidence.desc(), ComboRule.lift.desc())
        .limit(limit)
    ).scalars().all()

    return [
        {
            "antecedent_item": row.antecedent_item,
            "consequent_item": row.consequent_item,
            "confidence": float(row.confidence),
            "support": float(row.support),
            "lift": float(row.lift),
            "conviction": float(row.conviction) if row.conviction is not None else None,
            "leverage": float(row.leverage) if row.leverage is not None else None,
            "co_order_frequency": int(row.co_order_frequency) if row.co_order_frequency is not None else None,
        }
        for row in rows
    ]


def get_menu_items(
    db: Session,
    restaurant_id: str,
    menu_class: str | None = None,
    search: str | None = None,
) -> list[dict]:
    query = select(MenuMetric).where(MenuMetric.restaurant_id == restaurant_id)

    if menu_class:
        query = query.where(MenuMetric.menu_class == menu_class.upper())
    if search:
        query = query.where(MenuMetric.item_name.ilike(f"%{search}%"))

    query = query.order_by(MenuMetric.total_revenue.desc())
    metrics = db.execute(query).scalars().all()

    return [
        {
            "item_name": m.item_name,
            "menu_class": m.menu_class,
            "total_sales_qty": int(m.total_sales_qty),
            "total_revenue": float(m.total_revenue),
            "avg_margin": float(m.avg_margin),
            "sales_velocity": float(m.sales_velocity),
            "popularity_score": float(m.popularity_score),
            "margin_score": float(m.margin_score),
        }
        for m in metrics
    ]


def get_voice_logs(
    db: Session,
    restaurant_id: str,
    outcome: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query = select(VoiceCallLog).where(VoiceCallLog.restaurant_id == restaurant_id)
    if outcome:
        query = query.where(VoiceCallLog.outcome == outcome)
    query = query.order_by(VoiceCallLog.created_at.desc()).limit(limit)
    rows = db.execute(query).scalars().all()

    return [
        {
            "id": row.id,
            "call_id": row.call_id,
            "transcript": row.transcript,
            "outcome": row.outcome,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def get_failed_orders(db: Session, restaurant_id: str) -> list[dict]:
    rows = db.execute(
        select(FailedOrderQueue)
        .where(FailedOrderQueue.restaurant_id == restaurant_id)
        .order_by(FailedOrderQueue.created_at.desc())
    ).scalars().all()

    return [
        {
            "id": row.id,
            "call_id": row.call_id,
            "failure_reason": row.failure_reason,
            "retry_count": row.retry_count,
            "status": row.status,
            "created_at": row.created_at,
            "resolved_at": row.resolved_at,
        }
        for row in rows
    ]
