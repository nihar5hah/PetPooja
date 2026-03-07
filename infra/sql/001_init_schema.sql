CREATE TABLE IF NOT EXISTS pos_transactions (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  order_id VARCHAR(64) NOT NULL,
  transaction_date DATE NOT NULL,
  item_name VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL DEFAULT 'uncategorized',
  quantity INTEGER NOT NULL,
  unit_price DOUBLE PRECISION NOT NULL,
  food_cost_per_unit DOUBLE PRECISION NOT NULL,
  line_revenue DOUBLE PRECISION NOT NULL,
  line_contribution_margin DOUBLE PRECISION NOT NULL,
  ingested_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS menu_metrics (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  item_name VARCHAR(128) NOT NULL,
  total_sales_qty INTEGER NOT NULL,
  total_revenue DOUBLE PRECISION NOT NULL,
  avg_margin DOUBLE PRECISION NOT NULL,
  sales_velocity DOUBLE PRECISION NOT NULL,
  popularity_score DOUBLE PRECISION NOT NULL,
  margin_score DOUBLE PRECISION NOT NULL,
  menu_class VARCHAR(32) NOT NULL,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS combo_rules (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  antecedent_item VARCHAR(128) NOT NULL,
  consequent_item VARCHAR(128) NOT NULL,
  support DOUBLE PRECISION NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  lift DOUBLE PRECISION NOT NULL,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  source VARCHAR(32) NOT NULL DEFAULT 'voice',
  status VARCHAR(32) NOT NULL DEFAULT 'confirmed',
  customer_phone VARCHAR(32) NOT NULL DEFAULT '',
  total_amount DOUBLE PRECISION NOT NULL DEFAULT 0,
  call_id VARCHAR(128) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL,
  item_name VARCHAR(128) NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price DOUBLE PRECISION NOT NULL,
  line_total DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS menu_aliases (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  alias_text VARCHAR(128) NOT NULL,
  canonical_item_name VARCHAR(128) NOT NULL,
  confidence_hint DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS voice_call_logs (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  call_id VARCHAR(128) NOT NULL,
  transcript TEXT NOT NULL DEFAULT '',
  parsed_payload TEXT NOT NULL DEFAULT '{}',
  outcome VARCHAR(64) NOT NULL DEFAULT 'received',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS failed_order_queue (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id VARCHAR(64) NOT NULL DEFAULT 'default_restaurant',
  call_id VARCHAR(128) NOT NULL,
  payload TEXT NOT NULL,
  failure_reason TEXT NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_pos_txn_restaurant_order ON pos_transactions (restaurant_id, order_id);
CREATE INDEX IF NOT EXISTS idx_menu_metrics_restaurant_item ON menu_metrics (restaurant_id, item_name);
CREATE INDEX IF NOT EXISTS idx_combo_rules_restaurant_antecedent ON combo_rules (restaurant_id, antecedent_item);
