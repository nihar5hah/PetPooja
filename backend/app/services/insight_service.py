from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MenuMetric


INSIGHT_TEMPLATES = {
    "STAR": "{item} is a Star item (high margin, high popularity). Keep visible in top menu spots.",
    "PUZZLE": "{item} has high margin but low popularity. Promote it in combos and staff upsell scripts.",
    "CASH_COW": "{item} sells well but margin is lower. Protect volume while testing small price improvements.",
    "DOG": "{item} has low margin and low popularity. Consider recipe, pricing, or replacing it.",
}


def build_item_insight(item_name: str, menu_class: str) -> str:
    template = INSIGHT_TEMPLATES.get(menu_class, "{item} needs further analysis.")
    return template.format(item=item_name)


def get_menu_insights(db: Session, restaurant_id: str, limit: int = 100) -> list[dict]:
    metrics = db.execute(
        select(MenuMetric)
        .where(MenuMetric.restaurant_id == restaurant_id)
        .order_by(MenuMetric.total_revenue.desc())
        .limit(limit)
    ).scalars().all()

    results = []
    for metric in metrics:
        results.append(
            {
                "item_name": metric.item_name,
                "total_sales_qty": metric.total_sales_qty,
                "total_revenue": float(metric.total_revenue),
                "avg_margin": float(metric.avg_margin),
                "sales_velocity": float(metric.sales_velocity),
                "menu_class": metric.menu_class,
                "recommendation": build_item_insight(metric.item_name, metric.menu_class),
            }
        )

    return results
