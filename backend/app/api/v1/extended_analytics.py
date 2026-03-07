"""Extended analytics API endpoints — 10 metric categories."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.extended_schemas import (
    AdvancedBasketMetricsOut,
    CategoryMetricsOut,
    ComboPerformanceOut,
    ComboCardOut,
    ItemLevelMetricsOut,
    MenuMatrixViewOut,
    MenuEngineeringExtendedOut,
    OrderLevelMetricsOut,
    PopularityProfitabilityOut,
    PriceOptimizationOut,
    PricingCardOut,
    RestaurantKPIsOut,
    StrategyCardOut,
    UpsellCardOut,
    UpsellSignalOut,
)
from app.db.session import get_db
from app.services.extended_analytics_service import (
    get_advanced_basket_metrics,
    get_category_level_metrics,
    get_combo_performance,
    get_combo_cards,
    get_item_level_metrics,
    get_menu_matrix_view,
    get_menu_engineering_extended,
    get_order_level_metrics,
    get_popularity_profitability,
    get_price_optimization,
    get_pricing_cards,
    get_restaurant_kpis,
    get_strategy_cards,
    get_upsell_cards,
    get_upsell_signals,
)

router = APIRouter(prefix="/extended-analytics", tags=["Extended Analytics"])


@router.get("/order-metrics", response_model=list[OrderLevelMetricsOut])
def order_metrics(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_order_level_metrics(db, restaurant_id)


@router.get("/item-metrics", response_model=list[ItemLevelMetricsOut])
def item_metrics(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_item_level_metrics(db, restaurant_id)


@router.get("/category-metrics", response_model=list[CategoryMetricsOut])
def category_metrics(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_category_level_metrics(db, restaurant_id)


@router.get("/restaurant-kpis", response_model=RestaurantKPIsOut)
def restaurant_kpis(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_restaurant_kpis(db, restaurant_id)


@router.get("/menu-engineering-extended", response_model=list[MenuEngineeringExtendedOut])
def menu_engineering_extended(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_menu_engineering_extended(db, restaurant_id)


@router.get("/popularity-profitability", response_model=list[PopularityProfitabilityOut])
def popularity_profitability(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_popularity_profitability(db, restaurant_id)


@router.get("/basket-metrics", response_model=list[AdvancedBasketMetricsOut])
def basket_metrics(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_advanced_basket_metrics(db, restaurant_id)


@router.get("/combo-performance", response_model=list[ComboPerformanceOut])
def combo_performance(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_combo_performance(db, restaurant_id)


@router.get("/upsell-signals", response_model=list[UpsellSignalOut])
def upsell_signals(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_upsell_signals(db, restaurant_id)


@router.get("/price-optimization", response_model=list[PriceOptimizationOut])
def price_optimization(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_price_optimization(db, restaurant_id)


@router.get("/menu-matrix-view", response_model=MenuMatrixViewOut)
def menu_matrix_view(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_menu_matrix_view(db, restaurant_id)


@router.get("/combo-cards", response_model=list[ComboCardOut])
def combo_cards(
    restaurant_id: str = Query(default="default_restaurant"),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_combo_cards(db, restaurant_id, limit=limit)


@router.get("/upsell-cards", response_model=list[UpsellCardOut])
def upsell_cards(
    restaurant_id: str = Query(default="default_restaurant"),
    limit: int = Query(default=24, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_upsell_cards(db, restaurant_id, limit=limit)


@router.get("/pricing-cards", response_model=list[PricingCardOut])
def pricing_cards(
    restaurant_id: str = Query(default="default_restaurant"),
    db: Session = Depends(get_db),
):
    return get_pricing_cards(db, restaurant_id)


@router.get("/strategy-cards", response_model=list[StrategyCardOut])
def strategy_cards(
    restaurant_id: str = Query(default="default_restaurant"),
    strategy_type: str = Query(default="hidden_gems", pattern="^(hidden_gems|watch_list)$"),
    db: Session = Depends(get_db),
):
    return get_strategy_cards(db, restaurant_id, strategy_type=strategy_type)
