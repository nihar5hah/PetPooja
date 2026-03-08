import type {
  CategoryMetrics,
  ComboCard,
  ComboPerformance,
  DashboardCombo,
  DashboardMenuEngineering,
  DashboardSummary,
  FailedOrder,
  FailedOrderRetryResponse,
  IngestionResponse,
  ItemLevelMetrics,
  MenuMatrixView,
  MenuEngineeringExtended,
  MenuInsight,
  MenuItemDetail,
  Order,
  OrderLevelMetrics,
  PopularityProfitability,
  PriceOptimization,
  PricingCard,
  RecomputeParams,
  RecomputeResponse,
  RestaurantKPIs,
  StrategyCard,
  UpsellCard,
  UpsellSignal,
  VoiceCallLog,
  VoiceWebhookPayload,
  VoiceWebhookResponse,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const RESTAURANT_ID = process.env.NEXT_PUBLIC_RESTAURANT_ID || "default_restaurant";

function normalizeDashboardMenuEngineering(payload: unknown): DashboardMenuEngineering {
  const value = (payload ?? {}) as Partial<DashboardMenuEngineering>;
  return {
    buckets: Array.isArray(value.buckets) ? value.buckets : [],
    items: Array.isArray(value.items) ? value.items : [],
  };
}

function normalizeMenuMatrixView(payload: unknown): MenuMatrixView {
  const value = (payload ?? {}) as Partial<MenuMatrixView> & { quadrants?: Array<{ items?: unknown[] }> };
  return {
    units_median: typeof value.units_median === "number" ? value.units_median : 0,
    margin_median: typeof value.margin_median === "number" ? value.margin_median : 0,
    quadrants: Array.isArray(value.quadrants)
      ? value.quadrants.map((quadrant) => ({
          ...quadrant,
          items: Array.isArray(quadrant.items) ? quadrant.items : [],
        }))
      : [],
  } as MenuMatrixView;
}

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}

async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: body instanceof FormData ? {} : { "Content-Type": "application/json" },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API request failed: ${response.status} ${text}`);
  }

  return (await response.json()) as T;
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>(`/dashboard/summary?restaurant_id=${RESTAURANT_ID}`);
}

export function getMenuEngineering(): Promise<DashboardMenuEngineering> {
  return apiGet<DashboardMenuEngineering>(`/dashboard/menu-engineering?restaurant_id=${RESTAURANT_ID}`).then(
    normalizeDashboardMenuEngineering,
  );
}

export function getDashboardCombos(): Promise<DashboardCombo[]> {
  return apiGet<DashboardCombo[]>(`/dashboard/combos?restaurant_id=${RESTAURANT_ID}&limit=10`);
}

export function getMenuInsights(): Promise<MenuInsight[]> {
  return apiGet<MenuInsight[]>(`/menu-insights?restaurant_id=${RESTAURANT_ID}`);
}

export function getOrders(): Promise<Order[]> {
  return apiGet<Order[]>(`/orders?restaurant_id=${RESTAURANT_ID}&limit=50`);
}

export function getMenuItems(menuClass?: string, search?: string): Promise<MenuItemDetail[]> {
  const params = new URLSearchParams({ restaurant_id: RESTAURANT_ID });
  if (menuClass) params.set("menu_class", menuClass);
  if (search) params.set("search", search);
  return apiGet<MenuItemDetail[]>(`/dashboard/menu-items?${params}`);
}

export function getVoiceCallLogs(outcome?: string): Promise<VoiceCallLog[]> {
  const params = new URLSearchParams({ restaurant_id: RESTAURANT_ID, limit: "50" });
  if (outcome) params.set("outcome", outcome);
  return apiGet<VoiceCallLog[]>(`/dashboard/voice-logs?${params}`);
}

export function getFailedOrders(): Promise<FailedOrder[]> {
  return apiGet<FailedOrder[]>(`/dashboard/failed-orders?restaurant_id=${RESTAURANT_ID}`);
}

export function uploadPosCsv(file: File): Promise<IngestionResponse> {
  const form = new FormData();
  form.append("file", file);
  return apiPost<IngestionResponse>(`/ingestion/pos-transactions?restaurant_id=${RESTAURANT_ID}`, form);
}

export function recomputeAnalytics(params: RecomputeParams): Promise<RecomputeResponse> {
  const qs = new URLSearchParams({
    restaurant_id: RESTAURANT_ID,
    min_support: String(params.min_support),
    min_confidence: String(params.min_confidence),
    min_lift: String(params.min_lift),
    max_rules: String(params.max_rules),
  });
  return apiPost<RecomputeResponse>(`/analytics/recompute?${qs}`);
}

export function processVoiceOrder(payload: VoiceWebhookPayload): Promise<VoiceWebhookResponse> {
  return apiPost<VoiceWebhookResponse>("/voice/retell-webhook", {
    ...payload,
    restaurant_id: RESTAURANT_ID,
  });
}

export function retryFailedOrder(queueId: number): Promise<FailedOrderRetryResponse> {
  return apiPost<FailedOrderRetryResponse>(`/failed-orders/${queueId}/retry`);
}

// Extended Analytics API

export function getRestaurantKPIs(): Promise<RestaurantKPIs> {
  return apiGet<RestaurantKPIs>(`/extended-analytics/restaurant-kpis?restaurant_id=${RESTAURANT_ID}`);
}

export function getOrderLevelMetrics(): Promise<OrderLevelMetrics[]> {
  return apiGet<OrderLevelMetrics[]>(`/extended-analytics/order-metrics?restaurant_id=${RESTAURANT_ID}`);
}

export function getItemLevelMetrics(): Promise<ItemLevelMetrics[]> {
  return apiGet<ItemLevelMetrics[]>(`/extended-analytics/item-metrics?restaurant_id=${RESTAURANT_ID}`);
}

export function getCategoryMetrics(): Promise<CategoryMetrics[]> {
  return apiGet<CategoryMetrics[]>(`/extended-analytics/category-metrics?restaurant_id=${RESTAURANT_ID}`);
}

export function getMenuEngineeringExtended(): Promise<MenuEngineeringExtended[]> {
  return apiGet<MenuEngineeringExtended[]>(`/extended-analytics/menu-engineering-extended?restaurant_id=${RESTAURANT_ID}`);
}

export function getPopularityProfitability(): Promise<PopularityProfitability[]> {
  return apiGet<PopularityProfitability[]>(`/extended-analytics/popularity-profitability?restaurant_id=${RESTAURANT_ID}`);
}

export function getComboPerformance(): Promise<ComboPerformance[]> {
  return apiGet<ComboPerformance[]>(`/extended-analytics/combo-performance?restaurant_id=${RESTAURANT_ID}`);
}

export function getUpsellSignals(): Promise<UpsellSignal[]> {
  return apiGet<UpsellSignal[]>(`/extended-analytics/upsell-signals?restaurant_id=${RESTAURANT_ID}`);
}

export function getPriceOptimization(): Promise<PriceOptimization[]> {
  return apiGet<PriceOptimization[]>(`/extended-analytics/price-optimization?restaurant_id=${RESTAURANT_ID}`);
}

export function getMenuMatrixView(): Promise<MenuMatrixView> {
  return apiGet<MenuMatrixView>(`/extended-analytics/menu-matrix-view?restaurant_id=${RESTAURANT_ID}`).then(
    normalizeMenuMatrixView,
  );
}

export function getComboCards(limit = 30): Promise<ComboCard[]> {
  return apiGet<ComboCard[]>(`/extended-analytics/combo-cards?restaurant_id=${RESTAURANT_ID}&limit=${limit}`);
}

export function getUpsellCards(limit = 24): Promise<UpsellCard[]> {
  return apiGet<UpsellCard[]>(`/extended-analytics/upsell-cards?restaurant_id=${RESTAURANT_ID}&limit=${limit}`);
}

export function getPricingCards(): Promise<PricingCard[]> {
  return apiGet<PricingCard[]>(`/extended-analytics/pricing-cards?restaurant_id=${RESTAURANT_ID}`);
}

export function getStrategyCards(strategyType: "hidden_gems" | "watch_list"): Promise<StrategyCard[]> {
  return apiGet<StrategyCard[]>(`/extended-analytics/strategy-cards?restaurant_id=${RESTAURANT_ID}&strategy_type=${strategyType}`);
}
