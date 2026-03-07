from datetime import datetime

from pydantic import BaseModel, Field


class VoiceItemIn(BaseModel):
    item_name: str
    quantity: int = Field(default=1, ge=1)


class VoiceWebhookIn(BaseModel):
    restaurant_id: str = "default_restaurant"
    call_id: str
    customer_phone: str = ""
    transcript: str = ""
    ordered_items: list[VoiceItemIn] | None = None
    confirm_order: bool = False
    event_type: str = "call_update"


class ResolvedItemOut(BaseModel):
    item_name: str
    quantity: int
    confidence: float


class VoiceWebhookOut(BaseModel):
    status: str
    call_id: str
    needs_confirmation: bool
    resolved_items: list[ResolvedItemOut]
    unresolved_items: list[str]
    upsell_suggestions: list[dict]
    order_id: int | None = None
    message: str


class OrderOut(BaseModel):
    id: int
    restaurant_id: str
    source: str
    status: str
    customer_phone: str
    total_amount: float
    call_id: str
    created_at: datetime


class FailedOrderRetryOut(BaseModel):
    queue_id: int
    status: str
    order_id: int | None = None
    message: str
