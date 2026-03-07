export type TopSellingItem = {
  item_name: string;
  quantity: number;
};

export type DashboardSummary = {
  order_count: number;
  total_revenue: number;
  avg_order_value: number;
  top_selling_items: TopSellingItem[];
};

export type MenuEngineeringBucket = {
  menu_class: string;
  item_count: number;
};

export type MenuEngineeringItem = {
  item_name: string;
  menu_class: string;
  total_revenue: number;
  total_sales_qty: number;
};

export type DashboardMenuEngineering = {
  buckets: MenuEngineeringBucket[];
  items: MenuEngineeringItem[];
};

export type DashboardCombo = {
  antecedent_item: string;
  consequent_item: string;
  confidence: number;
  support: number;
  lift: number;
  conviction: number | null;
  leverage: number | null;
  co_order_frequency: number | null;
};

export type MenuInsight = {
  item_name: string;
  total_sales_qty: number;
  total_revenue: number;
  avg_margin: number;
  sales_velocity: number;
  menu_class: string;
  recommendation: string;
};

export type Order = {
  id: number;
  restaurant_id: string;
  source: string;
  status: string;
  customer_phone: string;
  total_amount: number;
  call_id: string;
  created_at: string;
};

export type MenuItemDetail = {
  item_name: string;
  menu_class: string;
  total_sales_qty: number;
  total_revenue: number;
  avg_margin: number;
  sales_velocity: number;
  popularity_score: number;
  margin_score: number;
};

export type VoiceCallLog = {
  id: number;
  call_id: string;
  transcript: string;
  outcome: string;
  created_at: string;
};

export type FailedOrder = {
  id: number;
  call_id: string;
  failure_reason: string;
  retry_count: number;
  status: string;
  created_at: string;
  resolved_at: string | null;
};

export type IngestionResponse = {
  restaurant_id: string;
  rows_received: number;
  rows_inserted: number;
};

export type RecomputeResponse = {
  restaurant_id: string;
  items_processed: number;
  combo_rules_generated: number;
  computed_at: string;
};

export type RecomputeParams = {
  min_support: number;
  min_confidence: number;
  min_lift: number;
  max_rules: number;
};

export type VoiceItemIn = {
  item_name: string;
  quantity: number;
};

export type VoiceWebhookPayload = {
  restaurant_id?: string;
  call_id: string;
  customer_phone?: string;
  transcript?: string;
  ordered_items?: VoiceItemIn[];
  confirm_order?: boolean;
  event_type?: string;
};

export type ResolvedItem = {
  item_name: string;
  quantity: number;
  confidence: number;
};

export type UpsellSuggestion = {
  base_item: string;
  suggested_item: string;
  confidence: number;
  expected_margin_uplift: number;
};

export type VoiceWebhookResponse = {
  status: string;
  call_id: string;
  needs_confirmation: boolean;
  resolved_items: ResolvedItem[];
  unresolved_items: string[];
  upsell_suggestions: UpsellSuggestion[];
  order_id: number | null;
  message: string;
};

export type FailedOrderRetryResponse = {
  queue_id: number;
  status: string;
  order_id: number | null;
  message: string;
};

// Extended Analytics Types

export type OrderLevelMetrics = {
  order_id: string;
  total_items: number;
  unique_items: number;
  order_revenue: number;
  order_food_cost: number;
  order_margin: number;
  avg_item_price: number;
};

export type ItemLevelMetrics = {
  item_name: string;
  total_qty_sold: number;
  total_revenue: number;
  total_margin: number;
  total_food_cost: number;
  avg_unit_price: number;
  avg_food_cost: number;
  avg_margin_per_unit: number;
  margin_pct: number;
  order_frequency: number;
  revenue_share_pct: number;
  sales_velocity: number;
  revenue_per_day: number;
  order_count: number;
};

export type CategoryMetrics = {
  category: string;
  item_count: number;
  total_qty_sold: number;
  total_revenue: number;
  total_margin: number;
  total_food_cost: number;
  avg_unit_price: number;
  order_count: number;
  revenue_share_pct: number;
  margin_share_pct: number;
  avg_margin_pct: number;
};

export type RestaurantKPIs = {
  total_orders: number;
  total_revenue: number;
  total_profit: number;
  avg_order_value: number;
  avg_profit_per_order: number;
  overall_margin_pct: number;
};

export type MenuEngineeringExtended = {
  item_name: string;
  menu_class: string;
  popularity_score: number;
  margin_score: number;
  revenue_share_pct: number;
  margin_pct: number;
  order_frequency: number;
  total_revenue: number;
  total_margin: number;
  avg_unit_price: number;
  revenue_rank: number;
  margin_rank: number;
  popularity_rank: number;
};

export type PopularityProfitability = {
  item_name: string;
  demand_index: number;
  profitability_index: number;
  total_qty: number;
  total_margin: number;
  order_count: number;
};

export type AdvancedBasketMetrics = {
  antecedent_item: string;
  consequent_item: string;
  support: number;
  confidence: number;
  lift: number;
  conviction: number | null;
  leverage: number | null;
  co_order_frequency: number | null;
};

export type ComboPerformance = {
  antecedent_item: string;
  consequent_item: string;
  confidence: number;
  lift: number;
  pair_avg_revenue: number;
  pair_avg_margin: number;
  co_order_avg_revenue: number;
  co_order_avg_margin: number;
};

export type UpsellSignal = {
  base_item: string;
  suggested_item: string;
  confidence: number;
  lift: number;
  expected_margin_uplift: number;
  price_delta: number;
  upsell_score: number;
};

export type PriceOptimization = {
  item_name: string;
  category: string;
  avg_price: number;
  avg_food_cost: number;
  cost_ratio: number;
  margin_per_unit: number;
  price_to_margin_ratio: number;
  demand_elasticity_proxy: number;
  price_vs_category_pct: number;
  category_avg_price: number;
};

export type MenuMatrixItem = {
  item_name: string;
  margin_pct: number;
};

export type MenuMatrixQuadrant = {
  key: string;
  title: string;
  description: string;
  count: number;
  items: MenuMatrixItem[];
};

export type MenuMatrixView = {
  units_median: number;
  margin_median: number;
  quadrants: MenuMatrixQuadrant[];
};

export type ComboCard = {
  primary_item: string;
  secondary_item: string;
  primary_category: string;
  secondary_category: string;
  same_cuisine: boolean;
  strength: string;
  lift: number;
  support: number;
  co_orders: number;
  avg_cm_pct: number;
  bundle_price: number;
  primary_to_secondary_confidence: number;
  secondary_to_primary_confidence: number;
};

export type UpsellSuggestionCard = {
  rank: number;
  item_name: string;
  category: string;
  co_order_count: number;
  margin_pct: number;
  confidence: number;
  lift: number;
};

export type UpsellCard = {
  base_item: string;
  category: string;
  suggestions: UpsellSuggestionCard[];
};

export type PricingCard = {
  item_name: string;
  category: string;
  priority: string;
  uplift_potential: number;
  current_price: number;
  current_cm_pct: number;
  suggested_price: number;
  target_cm_pct: number;
  delta_amount: number;
  delta_pct: number;
  volume_total: number;
  volume_per_day: number;
  cm_gap_pct: number;
  cm_gap_description: string;
};

export type StrategyCard = {
  item_name: string;
  category: string;
  margin_pct: number;
  units: number;
  revenue: number;
  profit: number;
  recommended_actions: string[];
};
