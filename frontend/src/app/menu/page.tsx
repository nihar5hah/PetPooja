"use client";

import { Suspense, startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Package, Search } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import type { Route } from "next";

import { PageHeader } from "@/components/ui/page-header";
import { MenuClassBadge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnimatedPage, EmptyState, SortableHeader, Spinner, Tabs } from "@/components/ui/data-display";
import { Input } from "@/components/ui/input";
import {
  getComboCards,
  getMenuInsights,
  getMenuItems,
  getMenuMatrixView,
  getPopularityProfitability,
  getPriceOptimization,
  getPricingCards,
  getStrategyCards,
  getUpsellCards,
} from "@/lib/api";
import type {
  ComboCard,
  MenuInsight,
  MenuItemDetail,
  MenuMatrixView,
  PopularityProfitability,
  PriceOptimization,
  PricingCard,
  StrategyCard,
  UpsellCard,
} from "@/lib/types";
import { CombosTab } from "@/app/menu/tabs/combos-tab";
import { HiddenGemsTab } from "@/app/menu/tabs/hidden-gems-tab";
import { MenuMatrixTab } from "@/app/menu/tabs/menu-matrix-tab";
import { PricingTab } from "@/app/menu/tabs/pricing-tab";
import { UpsellTab } from "@/app/menu/tabs/upsell-tab";
import { WatchListTab } from "@/app/menu/tabs/watch-list-tab";

const OVERVIEW_CLASSES = ["All", "STAR", "CASH_COW", "PUZZLE", "DOG"];
const CLASS_COLORS: Record<string, string> = {
  STAR: "#f59e0b",
  CASH_COW: "#22c55e",
  PUZZLE: "#8b5cf6",
  DOG: "#71717a",
};
const MENU_TABS = [
  { id: "overview", label: "Overview" },
  { id: "menu-matrix", label: "Menu Matrix" },
  { id: "combos", label: "Combos" },
  { id: "upsell", label: "Upsell" },
  { id: "pricing", label: "Pricing" },
  { id: "hidden-gems", label: "Hidden Gems" },
  { id: "watch-list", label: "Watch List" },
] as const;

type TabId = (typeof MENU_TABS)[number]["id"];
type SortKey = keyof MenuItemDetail;
type SortDir = "asc" | "desc";

function currency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function normalizeTab(value: string | null): TabId {
  const next = (value ?? "overview").toLowerCase();
  return (MENU_TABS.find((tab) => tab.id === next)?.id ?? "overview") as TabId;
}

function MenuPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<TabId>(() => normalizeTab(searchParams.get("tab")));
  const [items, setItems] = useState<MenuItemDetail[]>([]);
  const [insights, setInsights] = useState<MenuInsight[]>([]);
  const [priceOpt, setPriceOpt] = useState<PriceOptimization[]>([]);
  const [popProfit, setPopProfit] = useState<PopularityProfitability[]>([]);
  const [activeClass, setActiveClass] = useState("All");
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("total_revenue");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [menuMatrix, setMenuMatrix] = useState<MenuMatrixView | null>(null);
  const [comboCards, setComboCards] = useState<ComboCard[] | null>(null);
  const [upsellCards, setUpsellCards] = useState<UpsellCard[] | null>(null);
  const [pricingCards, setPricingCards] = useState<PricingCard[] | null>(null);
  const [hiddenGemsCards, setHiddenGemsCards] = useState<StrategyCard[] | null>(null);
  const [watchListCards, setWatchListCards] = useState<StrategyCard[] | null>(null);
  const [loadingTab, setLoadingTab] = useState<TabId | null>(null);
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    setActiveTab(normalizeTab(searchParams.get("tab")));
  }, [searchParams]);

  useEffect(() => {
    Promise.all([getMenuItems(), getMenuInsights(), getPriceOptimization(), getPopularityProfitability()])
      .then(([menuItems, menuInsights, pricing, popularity]) => {
        setItems(menuItems);
        setInsights(menuInsights);
        setPriceOpt(pricing);
        setPopProfit(popularity);
      })
      .finally(() => setOverviewLoading(false));
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadTabData() {
      if (activeTab === "overview") return;
      setLoadingTab(activeTab);
      try {
        if (activeTab === "menu-matrix" && !menuMatrix) {
          const data = await getMenuMatrixView();
          if (!cancelled) setMenuMatrix(data);
        }
        if (activeTab === "combos" && !comboCards) {
          const data = await getComboCards();
          if (!cancelled) setComboCards(data);
        }
        if (activeTab === "upsell" && !upsellCards) {
          const data = await getUpsellCards();
          if (!cancelled) setUpsellCards(data);
        }
        if (activeTab === "pricing" && !pricingCards) {
          const data = await getPricingCards();
          if (!cancelled) setPricingCards(data);
        }
        if (activeTab === "hidden-gems" && !hiddenGemsCards) {
          const data = await getStrategyCards("hidden_gems");
          if (!cancelled) setHiddenGemsCards(data);
        }
        if (activeTab === "watch-list" && !watchListCards) {
          const data = await getStrategyCards("watch_list");
          if (!cancelled) setWatchListCards(data);
        }
      } finally {
        if (!cancelled) setLoadingTab(null);
      }
    }

    void loadTabData();
    return () => {
      cancelled = true;
    };
  }, [activeTab, comboCards, hiddenGemsCards, menuMatrix, pricingCards, upsellCards, watchListCards]);

  const filtered = useMemo(() => {
    let list = items;
    if (activeClass !== "All") list = list.filter((item) => item.menu_class === activeClass);
    if (deferredSearch.trim()) {
      const query = deferredSearch.toLowerCase();
      list = list.filter((item) => item.item_name.toLowerCase().includes(query));
    }
    const dir = sortDir === "asc" ? 1 : -1;
    return [...list].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string") return dir * av.localeCompare(bv as string);
      return dir * ((av as number) - (bv as number));
    });
  }, [activeClass, deferredSearch, items, sortDir, sortKey]);

  const insightMap = useMemo(() => {
    const map = new Map<string, string>();
    insights.forEach((insight) => map.set(insight.item_name, insight.recommendation));
    return map;
  }, [insights]);

  const priceMap = useMemo(() => {
    const map = new Map<string, PriceOptimization>();
    priceOpt.forEach((item) => map.set(item.item_name, item));
    return map;
  }, [priceOpt]);

  const profitMap = useMemo(() => {
    const map = new Map<string, PopularityProfitability>();
    popProfit.forEach((item) => map.set(item.item_name, item));
    return map;
  }, [popProfit]);

  const scatterData = useMemo(
    () => items.map((item) => ({ name: item.item_name, x: item.popularity_score, y: item.margin_score, cls: item.menu_class })),
    [items],
  );

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((direction) => (direction === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  function handleTabChange(label: string) {
    const nextTab = MENU_TABS.find((tab) => tab.label === label)?.id ?? "overview";
    startTransition(() => {
      setActiveTab(nextTab);
      const nextParams = new URLSearchParams(searchParams.toString());
      if (nextTab === "overview") nextParams.delete("tab");
      else nextParams.set("tab", nextTab);
      const query = nextParams.toString();
      router.replace((query ? `/menu?${query}` : "/menu") as Route, { scroll: false });
    });
  }

  function renderOverview() {
    if (overviewLoading) return <Spinner />;

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Popularity vs Margin</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="x" name="Popularity" type="number" tick={{ fill: "#71717a", fontSize: 11 }} axisLine={{ stroke: "#27272a" }} />
                <YAxis dataKey="y" name="Margin" type="number" tick={{ fill: "#71717a", fontSize: 11 }} axisLine={{ stroke: "#27272a" }} />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  contentStyle={{
                    backgroundColor: "#111113",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#fafafa",
                  }}
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const point = payload[0].payload as (typeof scatterData)[number];
                    return (
                      <div className="rounded-lg border border-border bg-card p-3 text-xs shadow-lg">
                        <p className="font-semibold text-foreground">{point.name}</p>
                        <p className="mt-1 text-muted-foreground">Pop: {point.x.toFixed(3)} · Margin: {point.y.toFixed(0)}</p>
                        <MenuClassBadge value={point.cls} />
                      </div>
                    );
                  }}
                />
                <Scatter data={scatterData}>
                  {scatterData.map((point, index) => (
                    <Cell key={index} fill={CLASS_COLORS[point.cls] || "#555"} opacity={0.85} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <Tabs tabs={OVERVIEW_CLASSES} active={activeClass} onChange={setActiveClass} />
          <div className="relative sm:ml-auto">
            <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search items…" value={search} onChange={(event) => setSearch(event.target.value)} className="w-full pl-8 sm:w-56" />
          </div>
        </div>

        <Card>
          <CardContent className="pt-5">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <SortableHeader label="Item" active={sortKey === "item_name"} direction={sortDir} onClick={() => toggleSort("item_name")} />
                    <SortableHeader label="Class" active={sortKey === "menu_class"} direction={sortDir} onClick={() => toggleSort("menu_class")} />
                    <SortableHeader label="Qty Sold" active={sortKey === "total_sales_qty"} direction={sortDir} onClick={() => toggleSort("total_sales_qty")} className="text-right" />
                    <SortableHeader label="Revenue" active={sortKey === "total_revenue"} direction={sortDir} onClick={() => toggleSort("total_revenue")} className="text-right" />
                    <SortableHeader label="Margin" active={sortKey === "avg_margin"} direction={sortDir} onClick={() => toggleSort("avg_margin")} className="text-right" />
                    <SortableHeader label="Pop." active={sortKey === "popularity_score"} direction={sortDir} onClick={() => toggleSort("popularity_score")} className="text-right" />
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Demand</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Profit Idx</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Cost Ratio</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Recommendation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.map((item, index) => (
                    <motion.tr
                      key={item.item_name}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.015 }}
                      className="transition-colors hover:bg-muted/50"
                    >
                      <td className="px-3 py-2.5 text-xs font-medium">{item.item_name}</td>
                      <td className="px-3 py-2.5"><MenuClassBadge value={item.menu_class} /></td>
                      <td className="px-3 py-2.5 text-right text-xs tabular-nums">{item.total_sales_qty}</td>
                      <td className="px-3 py-2.5 text-right text-xs tabular-nums">{currency(item.total_revenue)}</td>
                      <td className="px-3 py-2.5 text-right text-xs tabular-nums">{(item.avg_margin * 100).toFixed(1)}%</td>
                      <td className="px-3 py-2.5 text-right text-xs tabular-nums">{item.popularity_score.toFixed(3)}</td>
                      <td className="px-3 py-2.5 text-xs tabular-nums">{profitMap.get(item.item_name)?.demand_index?.toFixed(3) ?? "—"}</td>
                      <td className="px-3 py-2.5 text-xs tabular-nums">{profitMap.get(item.item_name)?.profitability_index?.toFixed(3) ?? "—"}</td>
                      <td className="px-3 py-2.5 text-xs tabular-nums">
                        {priceMap.get(item.item_name)?.cost_ratio != null ? `${(priceMap.get(item.item_name)!.cost_ratio * 100).toFixed(1)}%` : "—"}
                      </td>
                      <td className="max-w-[260px] truncate px-3 py-2.5 text-xs text-muted-foreground">{insightMap.get(item.item_name) || "—"}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
            {filtered.length === 0 && (
              <EmptyState icon={<Package className="size-8" />} title="No items found" description="Try a different filter or search term." />
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  function renderActiveTab() {
    if (activeTab === "overview") return renderOverview();
    if (loadingTab === activeTab) return <Spinner />;
    if (activeTab === "menu-matrix" && menuMatrix) return <MenuMatrixTab data={menuMatrix} />;
    if (activeTab === "combos" && comboCards) return <CombosTab cards={comboCards} />;
    if (activeTab === "upsell" && upsellCards) return <UpsellTab cards={upsellCards} />;
    if (activeTab === "pricing" && pricingCards) return <PricingTab cards={pricingCards} />;
    if (activeTab === "hidden-gems" && hiddenGemsCards) return <HiddenGemsTab cards={hiddenGemsCards} />;
    if (activeTab === "watch-list" && watchListCards) return <WatchListTab cards={watchListCards} />;
    return <Spinner />;
  }

  return (
    <AnimatedPage>
      <PageHeader title="Menu Intelligence" description="Real-time menu engineering, pricing, bundle, and strategy views." />

      <div className="mb-6 overflow-x-auto">
        <Tabs tabs={MENU_TABS.map((tab) => tab.label)} active={MENU_TABS.find((tab) => tab.id === activeTab)?.label ?? "Overview"} onChange={handleTabChange} />
      </div>

      {renderActiveTab()}
    </AnimatedPage>
  );
}

export default function MenuPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <MenuPageContent />
    </Suspense>
  );
}
