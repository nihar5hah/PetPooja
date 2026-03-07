from datetime import datetime

from pydantic import BaseModel


class TopSellingItemOut(BaseModel):
    item_name: str
    quantity: int


class DashboardSummaryOut(BaseModel):
    order_count: int
    total_revenue: float
    avg_order_value: float
    top_selling_items: list[TopSellingItemOut]


class MenuEngineeringBucketOut(BaseModel):
    menu_class: str
    item_count: int


class MenuEngineeringItemOut(BaseModel):
    item_name: str
    menu_class: str
    total_revenue: float
    total_sales_qty: int


class DashboardMenuEngineeringOut(BaseModel):
    buckets: list[MenuEngineeringBucketOut]
    items: list[MenuEngineeringItemOut]


class DashboardComboOut(BaseModel):
    antecedent_item: str
    consequent_item: str
    confidence: float
    support: float
    lift: float
    conviction: float | None = None
    leverage: float | None = None
    co_order_frequency: int | None = None


class MenuItemDetailOut(BaseModel):
    item_name: str
    menu_class: str
    total_sales_qty: int
    total_revenue: float
    avg_margin: float
    sales_velocity: float
    popularity_score: float
    margin_score: float


class VoiceCallLogOut(BaseModel):
    id: int
    call_id: str
    transcript: str
    outcome: str
    created_at: datetime


class FailedOrderOut(BaseModel):
    id: int
    call_id: str
    failure_reason: str
    retry_count: int
    status: str
    created_at: datetime
    resolved_at: datetime | None = None
