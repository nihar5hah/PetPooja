"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";

import { Card, CardContent } from "@/components/ui/card";
import { Tabs } from "@/components/ui/data-display";
import type { ComboCard } from "@/lib/types";

const STRENGTH_TABS = ["All", "Strong", "Moderate", "Weak"];

function currency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function CombosTab({ cards }: { cards: ComboCard[] }) {
  const [activeStrength, setActiveStrength] = useState("All");

  const filtered = useMemo(() => {
    if (activeStrength === "All") return cards;
    return cards.filter((card) => card.strength === activeStrength);
  }, [activeStrength, cards]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">Cuisine-matched combo opportunities ranked by lift and confidence.</p>
        <Tabs tabs={STRENGTH_TABS} active={activeStrength} onChange={setActiveStrength} />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {filtered.map((card, index) => (
          <motion.div
            key={`${card.primary_item}-${card.secondary_item}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.03 }}
          >
            <Card className="h-full border-primary/15 bg-card/95">
              <CardContent className="space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-bold text-foreground">{card.primary_item} + {card.secondary_item}</h3>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className="rounded-md bg-info/10 px-2 py-1 text-[11px] font-semibold text-info">{card.primary_category}</span>
                      <span className="rounded-md bg-violet-500/10 px-2 py-1 text-[11px] font-semibold text-violet-300">{card.secondary_category}</span>
                      <span className="rounded-md bg-muted px-2 py-1 text-[11px] font-semibold text-muted-foreground">
                        {card.same_cuisine ? "same cuisine" : "cross cuisine"}
                      </span>
                    </div>
                  </div>
                  <span className="rounded-md border border-primary/20 bg-primary/10 px-2 py-1 text-[11px] font-semibold text-primary">
                    {card.strength}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-2 text-center text-xs">
                  <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-2 py-3 text-emerald-300">
                    <div className="text-xl font-bold">{card.lift.toFixed(1)}x</div>
                    <div className="text-[11px] uppercase tracking-wider">Lift</div>
                  </div>
                  <div className="rounded-xl border border-violet-500/20 bg-violet-500/10 px-2 py-3 text-violet-200">
                    <div className="text-xl font-bold">{(card.support * 100).toFixed(1)}%</div>
                    <div className="text-[11px] uppercase tracking-wider">Support</div>
                  </div>
                  <div className="rounded-xl border border-info/20 bg-info/10 px-2 py-3 text-info">
                    <div className="text-xl font-bold">{card.co_orders}</div>
                    <div className="text-[11px] uppercase tracking-wider">Co-orders</div>
                  </div>
                  <div className="rounded-xl border border-success/20 bg-success/10 px-2 py-3 text-success">
                    <div className="text-xl font-bold">{card.avg_cm_pct.toFixed(1)}%</div>
                    <div className="text-[11px] uppercase tracking-wider">Avg CM%</div>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-xl border border-border bg-background px-3 py-3 text-sm">
                  <span className="text-muted-foreground">Bundle price</span>
                  <span className="text-2xl font-bold text-primary">{currency(card.bundle_price)}</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs text-muted-foreground">
                  <div className="rounded-lg border border-border bg-background px-3 py-2">
                    <div>{card.primary_item} → {card.secondary_item}</div>
                    <div className="mt-1 text-lg font-bold text-foreground">{(card.primary_to_secondary_confidence * 100).toFixed(1)}%</div>
                  </div>
                  <div className="rounded-lg border border-border bg-background px-3 py-2">
                    <div>{card.secondary_item} → {card.primary_item}</div>
                    <div className="mt-1 text-lg font-bold text-foreground">{(card.secondary_to_primary_confidence * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}