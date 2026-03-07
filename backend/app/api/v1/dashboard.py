from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dashboard_schemas import (
    DashboardComboOut,
    DashboardMenuEngineeringOut,
    DashboardSummaryOut,
    FailedOrderOut,
    MenuItemDetailOut,
    VoiceCallLogOut,
)
from app.db.session import get_db
from app.services.dashboard_service import (
    get_dashboard_combos,
    get_dashboard_summary,
    get_failed_orders,
    get_menu_engineering,
    get_menu_items,
    get_voice_logs,
)


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummaryOut)
def dashboard_summary(
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(db, restaurant_id)


@router.get("/dashboard/menu-engineering", response_model=DashboardMenuEngineeringOut)
def dashboard_menu_engineering(
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    return get_menu_engineering(db, restaurant_id)


@router.get("/dashboard/combos", response_model=list[DashboardComboOut])
def dashboard_combos(
    restaurant_id: str = "default_restaurant",
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return get_dashboard_combos(db, restaurant_id, limit)


@router.get("/dashboard/menu-items", response_model=list[MenuItemDetailOut])
def dashboard_menu_items(
    restaurant_id: str = "default_restaurant",
    menu_class: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return get_menu_items(db, restaurant_id, menu_class=menu_class, search=search)


@router.get("/dashboard/voice-logs", response_model=list[VoiceCallLogOut])
def dashboard_voice_logs(
    restaurant_id: str = "default_restaurant",
    outcome: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return get_voice_logs(db, restaurant_id, outcome=outcome, limit=limit)


@router.get("/dashboard/failed-orders", response_model=list[FailedOrderOut])
def dashboard_failed_orders(
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    return get_failed_orders(db, restaurant_id)
