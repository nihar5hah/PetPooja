import { DashboardContent } from "@/app/dashboard-content";
import {
  getCategoryMetrics,
  getDashboardCombos,
  getDashboardSummary,
  getMenuEngineering,
  getMenuInsights,
  getOrders,
  getRestaurantKPIs,
} from "@/lib/api";

export default async function DashboardPage() {
  const [summary, menuEngineering, combos, insights, orders, kpis, categories] = await Promise.all([
    getDashboardSummary(),
    getMenuEngineering(),
    getDashboardCombos(),
    getMenuInsights(),
    getOrders(),
    getRestaurantKPIs(),
    getCategoryMetrics(),
  ]);

  return (
    <DashboardContent
      initialSummary={summary}
      initialMenuEng={menuEngineering}
      initialCombos={combos}
      initialInsights={insights}
      initialOrders={orders}
      initialKPIs={kpis}
      initialCategories={categories}
    />
  );
}
