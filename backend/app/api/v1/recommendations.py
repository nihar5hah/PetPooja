from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.association_service import classify_combo_strength, score_combo_rule
from app.db.models import ComboRule
from app.db.schemas import ComboRecommendationOut, MenuInsightOut, UpsellSuggestionOut
from app.db.session import get_db
from app.services.insight_service import get_menu_insights
from app.services.upsell_service import get_upsell_suggestions


router = APIRouter(tags=["recommendations"])


@router.get("/menu-insights", response_model=list[MenuInsightOut])
def menu_insights(
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    return get_menu_insights(db, restaurant_id)


@router.get("/combo-recommendations")
def combo_recommendations(
    item_name: str | None = None,
    restaurant_id: str = "default_restaurant",
    limit: int = 20,
    format: str = "detailed",
    db: Session = Depends(get_db),
):
    query = select(ComboRule).where(ComboRule.restaurant_id == restaurant_id)
    if item_name:
        query = query.where(ComboRule.antecedent_item == item_name)

    rows = db.execute(query.order_by(ComboRule.confidence.desc(), ComboRule.lift.desc()).limit(limit)).scalars().all()

    if format == "simple":
        ranked = sorted(
            rows,
            key=lambda row: float(row.combo_score) if row.combo_score is not None else score_combo_rule(float(row.confidence), float(row.lift), float(row.support)),
            reverse=True,
        )
        recommended = [
            row.consequent_item
            for row in ranked
            if (row.strength or classify_combo_strength(float(row.confidence), float(row.lift))) == "Strong"
        ][:limit]
        return {"recommended": recommended}

    return [
        ComboRecommendationOut(
            antecedent_item=row.antecedent_item,
            consequent_item=row.consequent_item,
            confidence=float(row.confidence),
            support=float(row.support),
            lift=float(row.lift),
        )
        for row in rows
    ]


@router.get("/upsell-suggestions", response_model=list[UpsellSuggestionOut])
def upsell_suggestions(
    item_name: str,
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    records = get_upsell_suggestions(db, restaurant_id, item_name)
    return [UpsellSuggestionOut(**record) for record in records]
