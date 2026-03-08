"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  RefreshCw,
  ShoppingBag,
  IndianRupee,
  TrendingUp,
  Crown,
  ArrowRight,
  Sparkles,
  Wallet,
  Percent,
  PiggyBank,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge, MenuClassBadge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataTable, EmptyState, Spinner } from "@/components/ui/data-display";
import { useRealtimeRefresh } from "@/hooks/use-realtime-refresh";
import {
  getDashboardCombos,
  getDashboardSummary,
  getMenuEngineering,
  getMenuInsights,
  getOrders,
  getRestaurantKPIs,
  getCategoryMetrics,
} from "@/lib/api";
import type {
  CategoryMetrics,
  DashboardCombo,
  DashboardMenuEngineering,
  DashboardSummary,
  MenuInsight,
  Order,
  RestaurantKPIs,
} from "@/lib/types";

const PIE_COLORS: Record<string, string> = {
  STAR: "#f59e0b",
  CASH_COW: "#22c55e",
  PUZZLE: "#8b5cf6",
  DOG: "#71717a",
};

function currency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

type Props = {
  initialSummary: DashboardSummary;
  initialMenuEng: DashboardMenuEngineering;
  initialCombos: DashboardCombo[];
  initialInsights: MenuInsight[];
  initialOrders: Order[];
  initialKPIs: RestaurantKPIs;
  initialCategories: CategoryMetrics[];
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

export function DashboardContent({
  initialSummary,
  initialMenuEng,
  initialCombos,
  initialInsights,
  initialOrders,
  initialKPIs,
  initialCategories,
}: Props) {
  const refreshKey = useRealtimeRefresh(["orders", "pos_transactions", "menu_metrics", "combo_rules"]);
  const [summary, setSummary] = useState(initialSummary);
  const [menuEng, setMenuEng] = useState(initialMenuEng);
  const [combos, setCombos] = useState(initialCombos);
  const [insights, setInsights] = useState(initialInsights);
  const [orders, setOrders] = useState(initialOrders);
  const [kpis, setKPIs] = useState(initialKPIs);
  const [categories, setCategories] = useState(initialCategories);
  const [loading, setLoading] = useState(false);
  const safeMenuEng = {
    buckets: Array.isArray(menuEng?.buckets) ? menuEng.buckets : [],
    items: Array.isArray(menuEng?.items) ? menuEng.items : [],
  };

  async function refresh() {
    setLoading(true);
    try {
      const [s, m, c, i, o, k, cat] = await Promise.all([
        getDashboardSummary(),
        getMenuEngineering(),
        getDashboardCombos(),
        getMenuInsights(),
        getOrders(),
        getRestaurantKPIs(),
        getCategoryMetrics(),
      ]);
      setSummary(s);
      setMenuEng(m);
      setCombos(c);
      setInsights(i);
      setOrders(o);
      setKPIs(k);
      setCategories(cat);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (refreshKey === 0) {
      return;
    }
    void refresh();
  }, [refreshKey]);

  const topItems = safeMenuEng.items.slice(0, 6).map((it) => ({
    name: it.item_name.length > 18 ? it.item_name.slice(0, 18) + "…" : it.item_name,
    revenue: it.total_revenue,
  }));

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Revenue intelligence overview"
        actions={
          <Button variant="secondary" size="sm" onClick={refresh} disabled={loading}>
            <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        }
      />

      {/* KPI Cards */}
      <motion.div
        variants={stagger}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6 mb-6"
      >
        <StatCard
          label="Total Orders"
          value={kpis.total_orders.toLocaleString()}
          icon={<ShoppingBag className="size-5" />}
        />
        <StatCard
          label="Revenue"
          value={currency(kpis.total_revenue)}
          icon={<IndianRupee className="size-5" />}
        />
        <StatCard
          label="Total Profit"
          value={currency(kpis.total_profit)}
          icon={<PiggyBank className="size-5" />}
        />
        <StatCard
          label="Avg Order Value"
          value={currency(kpis.avg_order_value)}
          icon={<TrendingUp className="size-5" />}
        />
        <StatCard
          label="Avg Profit/Order"
          value={currency(kpis.avg_profit_per_order)}
          icon={<Wallet className="size-5" />}
        />
        <StatCard
          label="Overall Margin"
          value={`${kpis.overall_margin_pct.toFixed(1)}%`}
          icon={<Percent className="size-5" />}
        />
      </motion.div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5 mb-6">
        {/* Pie chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Menu Engineering</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={safeMenuEng.buckets}
                  dataKey="item_count"
                  nameKey="menu_class"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  strokeWidth={2}
                  stroke="#09090b"
                >
                  {safeMenuEng.buckets.map((b) => (
                    <Cell key={b.menu_class} fill={PIE_COLORS[b.menu_class] ?? "#555"} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111113",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  itemStyle={{ color: "#fafafa" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap justify-center gap-3 mt-2">
              {safeMenuEng.buckets.map((b) => (
                <div key={b.menu_class} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <div
                    className="size-2.5 rounded-full"
                    style={{ backgroundColor: PIE_COLORS[b.menu_class] ?? "#555" }}
                  />
                  {b.menu_class}
                  <span className="font-semibold text-foreground">{b.item_count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bar chart */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Top Items by Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topItems} layout="vertical" margin={{ left: 0, right: 16 }}>
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={120}
                  tick={{ fill: "#a1a1aa", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111113",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  formatter={(v: number) => [currency(v), "Revenue"]}
                  cursor={{ fill: "rgba(245, 158, 11, 0.05)" }}
                />
                <Bar
                  dataKey="revenue"
                  fill="#f59e0b"
                  radius={[0, 4, 4, 0]}
                  barSize={18}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Category Revenue Breakdown */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Category Revenue Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categories.sort((a, b) => b.total_revenue - a.total_revenue)} margin={{ left: 0, right: 16 }}>
              <XAxis
                dataKey="category"
                tick={{ fill: "#a1a1aa", fontSize: 11 }}
                axisLine={{ stroke: "#27272a" }}
                tickLine={false}
              />
              <YAxis hide />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111113",
                  border: "1px solid #27272a",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(v: number, name: string) => [
                  currency(v),
                  name === "total_revenue" ? "Revenue" : "Profit",
                ]}
                cursor={{ fill: "rgba(245, 158, 11, 0.05)" }}
              />
              <Bar dataKey="total_revenue" fill="#f59e0b" radius={[4, 4, 0, 0]} barSize={24} name="total_revenue" />
              <Bar dataKey="total_margin" fill="#22c55e" radius={[4, 4, 0, 0]} barSize={24} name="total_margin" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Tables row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 mb-6">
        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Orders</CardTitle>
          </CardHeader>
          <CardContent className="pt-3">
            <DataTable headers={[
              { label: "ID" },
              { label: "Phone" },
              { label: "Status" },
              { label: "Total", className: "text-right" },
            ]}>
              {orders.slice(0, 6).map((o) => (
                <tr key={o.id} className="hover:bg-muted/50 transition-colors">
                  <td className="px-3 py-2.5 text-xs font-mono text-muted-foreground">#{o.id}</td>
                  <td className="px-3 py-2.5 text-xs">{o.customer_phone || "—"}</td>
                  <td className="px-3 py-2.5"><StatusBadge value={o.status} /></td>
                  <td className="px-3 py-2.5 text-xs text-right font-medium tabular-nums">{currency(o.total_amount)}</td>
                </tr>
              ))}
            </DataTable>
            {orders.length === 0 && (
              <EmptyState
                icon={<ShoppingBag className="size-8" />}
                title="No orders yet"
                description="Voice orders will appear here"
              />
            )}
          </CardContent>
        </Card>

        {/* Top Combos */}
        <Card>
          <CardHeader>
            <CardTitle>Top Combo Rules</CardTitle>
          </CardHeader>
          <CardContent className="pt-3">
            <DataTable headers={[
              { label: "If ordered" },
              { label: "" },
              { label: "Suggest" },
              { label: "Conf.", className: "text-right" },
              { label: "Lift", className: "text-right" },
            ]}>
              {combos.slice(0, 6).map((c) => (
                <tr key={`${c.antecedent_item}-${c.consequent_item}`} className="hover:bg-muted/50 transition-colors">
                  <td className="px-3 py-2.5 text-xs">{c.antecedent_item}</td>
                  <td className="px-3 py-2.5"><ArrowRight className="size-3 text-muted-foreground" /></td>
                  <td className="px-3 py-2.5 text-xs font-medium text-primary">{c.consequent_item}</td>
                  <td className="px-3 py-2.5 text-xs text-right tabular-nums">{(c.confidence * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2.5 text-xs text-right tabular-nums">{c.lift.toFixed(2)}</td>
                </tr>
              ))}
            </DataTable>
            {combos.length === 0 && (
              <EmptyState
                icon={<Sparkles className="size-8" />}
                title="No combo rules"
                description="Run recompute from Operations"
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Menu Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Menu Insights & Recommendations</CardTitle>
        </CardHeader>
        <CardContent className="pt-3">
          <DataTable headers={[
            { label: "Item" },
            { label: "Class" },
            { label: "Qty Sold", className: "text-right" },
            { label: "Revenue", className: "text-right" },
            { label: "Recommendation" },
          ]}>
            {insights.slice(0, 8).map((i) => (
              <tr key={i.item_name} className="hover:bg-muted/50 transition-colors">
                <td className="px-3 py-2.5 text-xs font-medium">{i.item_name}</td>
                <td className="px-3 py-2.5"><MenuClassBadge value={i.menu_class} /></td>
                <td className="px-3 py-2.5 text-xs text-right tabular-nums">{i.total_sales_qty}</td>
                <td className="px-3 py-2.5 text-xs text-right tabular-nums">{currency(i.total_revenue)}</td>
                <td className="px-3 py-2.5 text-xs text-muted-foreground max-w-xs truncate">{i.recommendation}</td>
              </tr>
            ))}
          </DataTable>
        </CardContent>
      </Card>
    </>
  );
}
