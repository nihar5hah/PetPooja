from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PosTransaction(Base):
    __tablename__ = "pos_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    order_id: Mapped[str] = mapped_column(String(64), index=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    transaction_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    item_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    item_name: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), default="uncategorized")
    subcategory: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    food_cost_per_unit: Mapped[float] = mapped_column(Float)
    line_revenue: Mapped[float] = mapped_column(Float)
    line_food_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    line_contribution_margin: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32), default="pos")
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MenuMetric(Base):
    __tablename__ = "menu_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    item_name: Mapped[str] = mapped_column(String(128), index=True)
    total_sales_qty: Mapped[int] = mapped_column(Integer)
    total_revenue: Mapped[float] = mapped_column(Float)
    avg_margin: Mapped[float] = mapped_column(Float)
    sales_velocity: Mapped[float] = mapped_column(Float)
    popularity_score: Mapped[float] = mapped_column(Float)
    margin_score: Mapped[float] = mapped_column(Float)
    menu_class: Mapped[str] = mapped_column(String(32), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComboRule(Base):
    __tablename__ = "combo_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    antecedent_item: Mapped[str] = mapped_column(String(128), index=True)
    consequent_item: Mapped[str] = mapped_column(String(128), index=True)
    support: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    lift: Mapped[float] = mapped_column(Float)
    conviction: Mapped[float | None] = mapped_column(Float, nullable=True)
    leverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    co_order_frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    combo_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strength: Mapped[str | None] = mapped_column(String(16), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MenuAlias(Base):
    __tablename__ = "menu_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    alias_text: Mapped[str] = mapped_column(String(128), index=True)
    canonical_item_name: Mapped[str] = mapped_column(String(128), index=True)
    confidence_hint: Mapped[float] = mapped_column(Float, default=1.0)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    external_order_id: Mapped[str | None] = mapped_column("order_id", String(64), index=True, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="voice")
    status: Mapped[str] = mapped_column(String(32), default="confirmed")
    customer_phone: Mapped[str] = mapped_column(String(32), default="")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    order_profit: Mapped[float] = mapped_column(Float, default=0.0)
    call_id: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, index=True)
    item_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    item_name: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    contribution_margin: Mapped[float] = mapped_column(Float, default=0.0)
    line_total: Mapped[float] = mapped_column(Float)


class VoiceCallLog(Base):
    __tablename__ = "voice_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    call_id: Mapped[str] = mapped_column(String(128), index=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    parsed_payload: Mapped[str] = mapped_column(Text, default="{}")
    outcome: Mapped[str] = mapped_column(String(64), default="received")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FailedOrderQueue(Base):
    __tablename__ = "failed_order_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, default="default_restaurant")
    call_id: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[str] = mapped_column(Text)
    failure_reason: Mapped[str] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


Index("idx_combo_lookup", ComboRule.restaurant_id, ComboRule.antecedent_item)
Index("idx_metric_lookup", MenuMetric.restaurant_id, MenuMetric.item_name)
