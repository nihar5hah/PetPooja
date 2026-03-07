from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ComboRule, MenuMetric


def get_upsell_suggestions(db: Session, restaurant_id: str, item_name: str, limit: int = 5) -> list[dict]:
    rules = db.execute(
        select(ComboRule)
        .where(ComboRule.restaurant_id == restaurant_id)
        .where(ComboRule.antecedent_item == item_name)
        .order_by(ComboRule.confidence.desc(), ComboRule.lift.desc())
        .limit(limit)
    ).scalars().all()

    if not rules:
        return []

    margins = {
        metric.item_name: metric.avg_margin
        for metric in db.execute(
            select(MenuMetric)
            .where(MenuMetric.restaurant_id == restaurant_id)
            .where(MenuMetric.item_name.in_([r.consequent_item for r in rules]))
        )
        .scalars()
        .all()
    }

    suggestions = []
    for rule in rules:
        suggestions.append(
            {
                "base_item": item_name,
                "suggested_item": rule.consequent_item,
                "confidence": float(rule.confidence),
                "expected_margin_uplift": float(margins.get(rule.consequent_item, 0.0)),
            }
        )

    return suggestions
