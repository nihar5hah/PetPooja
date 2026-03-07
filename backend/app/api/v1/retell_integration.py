from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.integration_schemas import (
    CreateOrderIn,
    CreateOrderOut,
    MenuItemOut,
    ValidateItemIn,
    ValidateItemOut,
)
from app.db.models import MenuAlias
from app.db.session import get_db
from app.services.dataset_context_service import load_full_menu_dataset
from app.services.order_service import create_integration_order
from app.services.voice_order_service import resolve_item_name


router = APIRouter(tags=["retell-integration"])


def _active_menu_candidates() -> list[str]:
    menu_df = load_full_menu_dataset()
    if menu_df.empty:
        return []
    return menu_df["item_name"].dropna().astype(str).tolist()


def _alias_map(db: Session, restaurant_id: str) -> dict[str, tuple[str, float]]:
    alias_rows = db.execute(
        select(MenuAlias.alias_text, MenuAlias.canonical_item_name, MenuAlias.confidence_hint).where(
            MenuAlias.restaurant_id == restaurant_id
        )
    ).all()
    return {str(alias_text).strip().lower(): (canonical_item_name, float(confidence_hint)) for alias_text, canonical_item_name, confidence_hint in alias_rows}


@router.get("/menu", response_model=list[MenuItemOut])
def get_menu_items():
    menu_df = load_full_menu_dataset()
    if menu_df.empty:
        return []

    return [
        MenuItemOut(
            item_id=str(rec["item_id"]) if rec.get("item_id") else None,
            item_name=str(rec["item_name"]),
            selling_price=float(rec["selling_price"]),
            category=str(rec["category"]),
        )
        for rec in menu_df[["item_id", "item_name", "selling_price", "category"]].to_dict(orient="records")
    ]


@router.post("/validate-item", response_model=ValidateItemOut)
def validate_item(
    payload: ValidateItemIn,
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    candidates = _active_menu_candidates()
    if not candidates:
        raise HTTPException(status_code=503, detail="Menu dataset is unavailable")

    matched_name, confidence = resolve_item_name(payload.item_name, candidates, _alias_map(db, restaurant_id))
    if matched_name and confidence >= 0.72:
        return ValidateItemOut(valid=True, matched_name=matched_name)

    suggested_name = matched_name if matched_name and confidence >= 0.5 else None
    return ValidateItemOut(valid=False, matched_name=None, suggested_name=suggested_name)


@router.post("/create-order", response_model=CreateOrderOut)
def create_order(
    payload: CreateOrderIn,
    restaurant_id: str = "default_restaurant",
    db: Session = Depends(get_db),
):
    candidates = _active_menu_candidates()
    if not candidates:
        raise HTTPException(status_code=503, detail="Menu dataset is unavailable")

    alias_map = _alias_map(db, restaurant_id)
    resolved_items: list[dict] = []
    invalid_items: list[str] = []

    for item in payload.items:
        matched_name, confidence = resolve_item_name(item.item_name, candidates, alias_map)
        if not matched_name or confidence < 0.72:
            invalid_items.append(item.item_name)
            continue
        resolved_items.append({"item_name": matched_name, "quantity": item.quantity})

    if invalid_items:
        raise HTTPException(status_code=400, detail={"invalid_items": invalid_items})

    try:
        order_id, order_value, order_profit, items_count, analytics_updated = create_integration_order(
            db=db,
            restaurant_id=restaurant_id,
            items=resolved_items,
            source=payload.source,
            customer_phone=payload.customer_phone,
            call_id=payload.call_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CreateOrderOut(
        order_id=order_id,
        order_value=order_value,
        order_profit=order_profit,
        items_count=items_count,
        analytics_updated=analytics_updated,
    )