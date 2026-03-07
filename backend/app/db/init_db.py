from sqlalchemy import text

from app.db import models  # noqa: F401
from app.db.session import Base, engine


DDL_STATEMENTS = [
    "ALTER TABLE pos_transactions ADD COLUMN IF NOT EXISTS transaction_time TIME NULL",
    "ALTER TABLE pos_transactions ADD COLUMN IF NOT EXISTS item_id VARCHAR(64) NULL",
    "ALTER TABLE pos_transactions ADD COLUMN IF NOT EXISTS subcategory VARCHAR(64) NULL",
    "ALTER TABLE pos_transactions ADD COLUMN IF NOT EXISTS line_food_cost DOUBLE PRECISION NULL",
    "ALTER TABLE pos_transactions ADD COLUMN IF NOT EXISTS source VARCHAR(32) NOT NULL DEFAULT 'pos'",
    "ALTER TABLE combo_rules ADD COLUMN IF NOT EXISTS combo_score DOUBLE PRECISION NULL",
    "ALTER TABLE combo_rules ADD COLUMN IF NOT EXISTS strength VARCHAR(16) NULL",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_id VARCHAR(64) NULL",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_profit DOUBLE PRECISION NOT NULL DEFAULT 0",
    "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS item_id VARCHAR(64) NULL",
    "ALTER TABLE order_items ADD COLUMN IF NOT EXISTS contribution_margin DOUBLE PRECISION NOT NULL DEFAULT 0",
]


def ensure_integration_schema() -> None:
    with engine.begin() as connection:
        for ddl in DDL_STATEMENTS:
            connection.execute(text(ddl))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_integration_schema()


if __name__ == "__main__":
    init_db()
