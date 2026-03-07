from __future__ import annotations

import json
from datetime import UTC, date, datetime, time
from secrets import randbelow

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FailedOrderQueue, Order, OrderItem, PosTransaction
from app.services.analytics_service import recompute_menu_metrics
from app.services.association_service import recompute_combo_rules
from app.services.dataset_context_service import get_menu_item_fallback


def _latest_unit_price_map(db: Session, item_names: list[str]) -> dict[str, float]:
    if not item_names:
        return {}

    rows = db.execute(
        select(PosTransaction.item_name, PosTransaction.unit_price, PosTransaction.id)
        .where(PosTransaction.item_name.in_(item_names))
        .order_by(PosTransaction.id.desc())
    ).all()

    price_map: dict[str, float] = {}
    for item_name, unit_price, _ in rows:
        if item_name not in price_map:
            price_map[item_name] = float(unit_price)

    for item_name in item_names:
        if item_name in price_map:
            continue
        fallback = get_menu_item_fallback(item_name)
        if fallback:
            price_map[item_name] = float(fallback["selling_price"])
    return price_map


def persist_order(
    db: Session,
    restaurant_id: str,
    call_id: str,
    customer_phone: str,
    resolved_items: list[dict],
    source: str = "voice",
    max_retries: int = 3,
) -> tuple[int | None, float, str | None]:
    attempt = 0
    while attempt < max_retries:
        try:
            price_map = _latest_unit_price_map(db, [item["item_name"] for item in resolved_items])

            total_amount = 0.0
            for item in resolved_items:
                unit_price = float(price_map.get(item["item_name"], 0.0))
                total_amount += unit_price * int(item["quantity"])

            order = Order(
                restaurant_id=restaurant_id,
                source=source,
                status="confirmed",
                customer_phone=customer_phone,
                total_amount=total_amount,
                call_id=call_id,
                created_at=datetime.now(UTC),
            )
            db.add(order)
            db.flush()

            for item in resolved_items:
                unit_price = float(price_map.get(item["item_name"], 0.0))
                db.add(
                    OrderItem(
                        order_id=order.id,
                        item_name=item["item_name"],
                        quantity=int(item["quantity"]),
                        unit_price=unit_price,
                        line_total=unit_price * int(item["quantity"]),
                    )
                )

            db.commit()
            db.refresh(order)
            return order.id, total_amount, None
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            attempt += 1
            if attempt >= max_retries:
                return None, 0.0, str(exc)

    return None, 0.0, "order persistence failed"


def _build_external_order_id(source: str) -> str:
    prefix = "VOICE" if source == "voice_agent" else source.upper().replace(" ", "_")
    return f"{prefix}_{int(datetime.now(UTC).timestamp())}_{1000 + randbelow(9000)}"


def create_integration_order(
    db: Session,
    restaurant_id: str,
    items: list[dict],
    source: str = "voice_agent",
    customer_phone: str = "",
    call_id: str | None = None,
) -> tuple[str, float, float, int, bool]:
    external_order_id = _build_external_order_id(source)
    order_value = 0.0
    order_profit = 0.0
    now = datetime.now(UTC)
    transaction_date = now.date()
    transaction_time = time(hour=now.hour, minute=now.minute, second=now.second)

    normalized_items: list[dict] = []
    for item in items:
        fallback = get_menu_item_fallback(str(item["item_name"]))
        if not fallback:
            raise ValueError(f"Unknown menu item: {item['item_name']}")

        quantity = int(item.get("quantity", 1))
        unit_price = float(fallback.get("selling_price", 0.0))
        unit_food_cost = float(fallback.get("food_cost", 0.0))
        unit_margin = float(fallback.get("contribution_margin", unit_price - unit_food_cost))
        line_revenue = unit_price * quantity
        line_food_cost = unit_food_cost * quantity
        line_contribution_margin = unit_margin * quantity

        order_value += line_revenue
        order_profit += line_contribution_margin

        normalized_items.append(
            {
                "item_id": str(fallback.get("item_id") or ""),
                "item_name": str(fallback["item_name"]),
                "category": str(fallback.get("category") or "uncategorized"),
                "subcategory": str(fallback.get("subcategory") or ""),
                "quantity": quantity,
                "unit_price": unit_price,
                "food_cost_per_unit": unit_food_cost,
                "line_revenue": line_revenue,
                "line_food_cost": line_food_cost,
                "line_contribution_margin": line_contribution_margin,
            }
        )

    order = Order(
        restaurant_id=restaurant_id,
        external_order_id=external_order_id,
        source=source,
        status="confirmed",
        customer_phone=customer_phone,
        total_amount=order_value,
        order_profit=order_profit,
        call_id=call_id or external_order_id,
        created_at=now,
    )
    db.add(order)
    db.flush()

    for item in normalized_items:
        db.add(
            OrderItem(
                order_id=order.id,
                item_id=item["item_id"] or None,
                item_name=item["item_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                contribution_margin=item["line_contribution_margin"],
                line_total=item["line_revenue"],
            )
        )
        db.add(
            PosTransaction(
                restaurant_id=restaurant_id,
                order_id=external_order_id,
                transaction_date=transaction_date,
                transaction_time=transaction_time,
                item_id=item["item_id"] or None,
                item_name=item["item_name"],
                category=item["category"],
                subcategory=item["subcategory"] or None,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                food_cost_per_unit=item["food_cost_per_unit"],
                line_revenue=item["line_revenue"],
                line_food_cost=item["line_food_cost"],
                line_contribution_margin=item["line_contribution_margin"],
                source=source,
                ingested_at=now,
            )
        )

    db.commit()

    analytics_updated = True
    try:
        recompute_menu_metrics(db, restaurant_id)
        recompute_combo_rules(
            db,
            restaurant_id,
            min_support=0.0005,
            min_confidence=0.05,
            min_lift=0.5,
            max_rules=200,
        )
    except Exception:  # noqa: BLE001
        analytics_updated = False

    return external_order_id, order_value, order_profit, sum(item["quantity"] for item in normalized_items), analytics_updated


def enqueue_failed_order(
    db: Session,
    restaurant_id: str,
    call_id: str,
    payload: dict,
    failure_reason: str,
    retry_count: int,
) -> int:
    queued = FailedOrderQueue(
        restaurant_id=restaurant_id,
        call_id=call_id,
        payload=json.dumps(payload),
        failure_reason=failure_reason,
        retry_count=retry_count,
        status="pending",
        created_at=datetime.now(UTC),
    )
    db.add(queued)
    db.commit()
    db.refresh(queued)
    return queued.id


def list_orders(db: Session, restaurant_id: str, limit: int = 50) -> list[Order]:
    return db.execute(
        select(Order)
        .where(Order.restaurant_id == restaurant_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    ).scalars().all()
