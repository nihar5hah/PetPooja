"use client";

import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Sparkles, Package, DollarSign } from "lucide-react";
import { getDashboardCombos, getMenuItems, getComboPerformance, getUpsellSignals } from "@/lib/api";
import type { DashboardCombo, MenuItemDetail, ComboPerformance, UpsellSignal } from "@/lib/types";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/input";
import {
  SortableHeader,
  ConfidenceBar,
  EmptyState,
  Spinner,
  AnimatedPage,
} from "@/components/ui/data-display";

type SortKey = "confidence" | "lift" | "support" | "antecedent_item" | "conviction" | "leverage";
type SortDir = "asc" | "desc";

function currency(v: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(v);
}

export default function CombosPage() {
  const [combos, setCombos] = useState<DashboardCombo[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItemDetail[]>([]);
  const [comboPerf, setComboPerf] = useState<ComboPerformance[]>([]);
  const [upsellSignals, setUpsellSignals] = useState<UpsellSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("confidence");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [selectedItem, setSelectedItem] = useState("");

  useEffect(() => {
    Promise.all([getDashboardCombos(), getMenuItems(), getComboPerformance(), getUpsellSignals()])
      .then(([c, m, cp, us]) => {
        setCombos(c);
        setMenuItems(m);
        setComboPerf(cp);
        setUpsellSignals(us);
      })
      .finally(() => setLoading(false));
  }, []);

  const sorted = useMemo(() => {
    const dir = sortDir === "asc" ? 1 : -1;
    return [...combos].sort((a, b) => {
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      if (typeof av === "string") return dir * av.localeCompare(bv as string);
      return dir * ((av as number) - (bv as number));
    });
  }, [combos, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const upsells = useMemo(() => {
    if (!selectedItem) return [];
    return upsellSignals.filter((u) => u.base_item === selectedItem);
  }, [upsellSignals, selectedItem]);

  const perfMap = useMemo(() => {
    const m = new Map<string, ComboPerformance>();
    comboPerf.forEach((p) => m.set(`${p.antecedent_item}-${p.consequent_item}`, p));
    return m;
  }, [comboPerf]);

  if (loading) return <Spinner />;

  return (
    <AnimatedPage>
      <PageHeader title="Combos & Upsells" description="Association rules mined from POS transaction data" />

      {/* Upsell Simulator */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="size-4 text-primary" />
            Upsell Simulator
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">
            Select a menu item to see what customers often buy alongside it.
          </p>
          <Select
            value={selectedItem}
            onChange={(e) => setSelectedItem(e.target.value)}
            className="max-w-xs"
          >
            <option value="">Choose an item…</option>
            {menuItems.map((m) => (
              <option key={m.item_name} value={m.item_name}>
                {m.item_name}
              </option>
            ))}
          </Select>

          {selectedItem && upsells.length > 0 && (
            <div className="overflow-x-auto mt-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Suggested Upsell</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Confidence</th>
                    <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Lift</th>
                    <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Margin Uplift</th>
                    <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {upsells.map((u, idx) => (
                    <motion.tr
                      key={u.suggested_item}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="hover:bg-muted/50 transition-colors"
                    >
                      <td className="px-3 py-2.5 text-xs font-medium">{u.suggested_item}</td>
                      <td className="px-3 py-2.5"><ConfidenceBar value={u.confidence} /></td>
                      <td className="px-3 py-2.5 text-xs text-right tabular-nums">{u.lift.toFixed(2)}</td>
                      <td className="px-3 py-2.5 text-xs text-right tabular-nums">{currency(u.expected_margin_uplift)}</td>
                      <td className="px-3 py-2.5 text-xs text-right tabular-nums font-medium text-primary">{u.upsell_score.toFixed(1)}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {selectedItem && upsells.length === 0 && (
            <p className="mt-3 text-sm text-muted-foreground">
              No upsell signals found for <span className="font-semibold text-foreground">{selectedItem}</span>.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Full rules table */}
      <Card>
        <CardHeader>
          <CardTitle>All Association Rules ({combos.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <SortableHeader label="If Customer Orders" active={sortKey === "antecedent_item"} direction={sortDir} onClick={() => toggleSort("antecedent_item")} />
                  <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Then Suggest</th>
                  <SortableHeader label="Confidence" active={sortKey === "confidence"} direction={sortDir} onClick={() => toggleSort("confidence")} />
                  <SortableHeader label="Support" active={sortKey === "support"} direction={sortDir} onClick={() => toggleSort("support")} className="text-right" />
                  <SortableHeader label="Lift" active={sortKey === "lift"} direction={sortDir} onClick={() => toggleSort("lift")} className="text-right" />
                  <SortableHeader label="Conviction" active={sortKey === "conviction"} direction={sortDir} onClick={() => toggleSort("conviction")} className="text-right" />
                  <SortableHeader label="Leverage" active={sortKey === "leverage"} direction={sortDir} onClick={() => toggleSort("leverage")} className="text-right" />
                  <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Pair Revenue</th>
                  <th className="px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Pair Margin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {sorted.map((c, idx) => (
                  <motion.tr
                    key={`${c.antecedent_item}-${c.consequent_item}`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.015 }}
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <td className="px-3 py-2.5 text-xs">{c.antecedent_item}</td>
                    <td className="px-3 py-2.5 text-xs font-semibold">{c.consequent_item}</td>
                    <td className="px-3 py-2.5"><ConfidenceBar value={c.confidence} /></td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{(c.support * 100).toFixed(3)}%</td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{c.lift.toFixed(2)}</td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{c.conviction?.toFixed(2) ?? "—"}</td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{c.leverage?.toFixed(4) ?? "—"}</td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{perfMap.get(`${c.antecedent_item}-${c.consequent_item}`)?.pair_avg_revenue != null ? currency(perfMap.get(`${c.antecedent_item}-${c.consequent_item}`)!.pair_avg_revenue) : "—"}</td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{perfMap.get(`${c.antecedent_item}-${c.consequent_item}`)?.pair_avg_margin != null ? currency(perfMap.get(`${c.antecedent_item}-${c.consequent_item}`)!.pair_avg_margin) : "—"}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          {combos.length === 0 && (
            <EmptyState
              icon={<Package className="size-8" />}
              title="No combo rules"
              description='Run "Recompute Analytics" from the Operations page to generate association rules.'
            />
          )}
        </CardContent>
      </Card>
    </AnimatedPage>
  );
}
