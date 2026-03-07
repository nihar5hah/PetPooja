from pydantic import BaseModel, Field


class MenuItemOut(BaseModel):
    item_id: str | None = None
    item_name: str
    selling_price: float
    category: str


class ValidateItemIn(BaseModel):
    item_name: str = Field(min_length=1)


class ValidateItemOut(BaseModel):
    valid: bool
    matched_name: str | None = None
    suggested_name: str | None = None


class ComboRecommendationSimpleOut(BaseModel):
    recommended: list[str]


class CreateOrderItemIn(BaseModel):
    item_name: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)


class CreateOrderIn(BaseModel):
    items: list[CreateOrderItemIn] = Field(min_length=1)
    source: str = "voice_agent"
    customer_phone: str = ""
    call_id: str | None = None


class CreateOrderOut(BaseModel):
    order_id: str
    order_value: float
    order_profit: float
    items_count: int
    analytics_updated: bool = True