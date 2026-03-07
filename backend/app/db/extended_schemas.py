"""Pydantic response schemas for extended analytics endpoints."""

from pydantic import BaseModel


class OrderLevelMetricsOut(BaseModel):
    order_id: str
    total_items: int
    unique_items: int
    order_revenue: float
    order_food_cost: float
    order_margin: float
    avg_item_price: float


class ItemLevelMetricsOut(BaseModel):
    item_name: str
    total_qty_sold: int
    total_revenue: float
    total_margin: float
    total_food_cost: float
    avg_unit_price: float
    avg_food_cost: float
    avg_margin_per_unit: float
    margin_pct: float
    order_frequency: float
    revenue_share_pct: float
    sales_velocity: float
    revenue_per_day: float
    order_count: int


class CategoryMetricsOut(BaseModel):
    category: str
    item_count: int
    total_qty_sold: int
    total_revenue: float
    total_margin: float
    total_food_cost: float
    avg_unit_price: float
    order_count: int
    revenue_share_pct: float
    margin_share_pct: float
    avg_margin_pct: float


class RestaurantKPIsOut(BaseModel):
    total_orders: int
    total_revenue: float
    total_profit: float
    avg_order_value: float
    avg_profit_per_order: float
    overall_margin_pct: float


class MenuEngineeringExtendedOut(BaseModel):
    item_name: str
    menu_class: str
    popularity_score: float
    margin_score: float
    revenue_share_pct: float
    margin_pct: float
    order_frequency: float
    total_revenue: float
    total_margin: float
    avg_unit_price: float
    revenue_rank: int
    margin_rank: int
    popularity_rank: int


class PopularityProfitabilityOut(BaseModel):
    item_name: str
    demand_index: float
    profitability_index: float
    total_qty: int
    total_margin: float
    order_count: int


class AdvancedBasketMetricsOut(BaseModel):
    antecedent_item: str
    consequent_item: str
    support: float
    confidence: float
    lift: float
    conviction: float | None = None
    leverage: float | None = None
    co_order_frequency: int | None = None


class ComboPerformanceOut(BaseModel):
    antecedent_item: str
    consequent_item: str
    confidence: float
    lift: float
    pair_avg_revenue: float
    pair_avg_margin: float
    co_order_avg_revenue: float
    co_order_avg_margin: float


class UpsellSignalOut(BaseModel):
    base_item: str
    suggested_item: str
    confidence: float
    lift: float
    expected_margin_uplift: float
    price_delta: float
    upsell_score: float


class PriceOptimizationOut(BaseModel):
    item_name: str
    category: str
    avg_price: float
    avg_food_cost: float
    cost_ratio: float
    margin_per_unit: float
    price_to_margin_ratio: float
    demand_elasticity_proxy: float
    price_vs_category_pct: float
    category_avg_price: float


class MenuMatrixItemOut(BaseModel):
    item_name: str
    margin_pct: float


class MenuMatrixQuadrantOut(BaseModel):
    key: str
    title: str
    description: str
    count: int
    items: list[MenuMatrixItemOut]


class MenuMatrixViewOut(BaseModel):
    units_median: float
    margin_median: float
    quadrants: list[MenuMatrixQuadrantOut]


class ComboCardOut(BaseModel):
    primary_item: str
    secondary_item: str
    primary_category: str
    secondary_category: str
    same_cuisine: bool
    strength: str
    lift: float
    support: float
    co_orders: int
    avg_cm_pct: float
    bundle_price: float
    primary_to_secondary_confidence: float
    secondary_to_primary_confidence: float


class UpsellSuggestionCardOut(BaseModel):
    rank: int
    item_name: str
    category: str
    co_order_count: int
    margin_pct: float
    confidence: float
    lift: float


class UpsellCardOut(BaseModel):
    base_item: str
    category: str
    suggestions: list[UpsellSuggestionCardOut]


class PricingCardOut(BaseModel):
    item_name: str
    category: str
    priority: str
    uplift_potential: float
    current_price: float
    current_cm_pct: float
    suggested_price: float
    target_cm_pct: float
    delta_amount: float
    delta_pct: float
    volume_total: int
    volume_per_day: float
    cm_gap_pct: float
    cm_gap_description: str


class StrategyCardOut(BaseModel):
    item_name: str
    category: str
    margin_pct: float
    units: int
    revenue: float
    profit: float
    recommended_actions: list[str]
