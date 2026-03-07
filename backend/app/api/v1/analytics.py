from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.schemas import RecomputeResponse
from app.db.session import get_db
from app.services.analytics_service import recompute_menu_metrics
from app.services.association_service import recompute_combo_rules


router = APIRouter(tags=["analytics"])


@router.post("/analytics/recompute", response_model=RecomputeResponse)
def recompute_analytics(
    restaurant_id: str = "default_restaurant",
    min_support: float = Query(default=0.001, ge=0.0005, le=0.5),
    min_confidence: float = Query(default=0.15, ge=0.05, le=1.0),
    min_lift: float = Query(default=1.0, ge=0.1, le=20.0),
    max_rules: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    items_processed, computed_at = recompute_menu_metrics(db, restaurant_id)
    combo_rules_generated, _ = recompute_combo_rules(
        db, restaurant_id,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_rules=max_rules,
    )

    return RecomputeResponse(
        restaurant_id=restaurant_id,
        items_processed=items_processed,
        combo_rules_generated=combo_rules_generated,
        computed_at=computed_at,
    )
