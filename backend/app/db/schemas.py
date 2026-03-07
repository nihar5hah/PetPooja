from datetime import date, datetime

from pydantic import BaseModel, Field


class MenuInsightOut(BaseModel):
    item_name: str
    total_sales_qty: int
    total_revenue: float
    avg_margin: float
    sales_velocity: float
    menu_class: str
    recommendation: str


class ComboRecommendationOut(BaseModel):
    antecedent_item: str
    consequent_item: str
    confidence: float
    support: float
    lift: float


class UpsellSuggestionOut(BaseModel):
    base_item: str
    suggested_item: str
    confidence: float
    expected_margin_uplift: float


class RecomputeResponse(BaseModel):
    restaurant_id: str
    items_processed: int
    combo_rules_generated: int
    computed_at: datetime


class IngestionResponse(BaseModel):
    restaurant_id: str
    rows_received: int
    rows_inserted: int


class PosTransactionIn(BaseModel):
    order_id: str
    transaction_date: date
    item_name: str
    category: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    food_cost_per_unit: float = Field(ge=0)
