"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";

import { Card, CardContent } from "@/components/ui/card";
import { Tabs } from "@/components/ui/data-display";
import type { PricingCard } from "@/lib/types";

const PRIORITY_TABS = ["All", "High", "Medium", "Low"];

function currency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

const PRIORITY_STYLES: Record<string, string> = {
  High: "border-rose-500/25 bg-rose-500/10 text-rose-300",
  Medium: "border-amber-500/25 bg-amber-500/10 text-amber-300",
  Low: "border-zinc-500/25 bg-zinc-500/10 text-zinc-300",
};

export function PricingTab({ cards }: { cards: PricingCard[] }) {
  const [priority, setPriority] = useState("All");

  const filtered = useMemo(() => {
    if (priority === "All") return cards;
    return cards.filter((card) => card.priority === priority);
  }, [cards, priority]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">Items trading below category margin expectation with estimated price uplift potential.</p>
        <Tabs tabs={PRIORITY_TABS} active={priority} onChange={setPriority} />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {filtered.map((card, index) => (
          <motion.div
            key={card.item_name}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.03 }}
          >
            <Card className="h-full border-primary/15 bg-card/95">
              <CardContent className="space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-bold text-foreground">{card.item_name}</h3>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className={`rounded-md border px-2 py-1 text-[11px] font-semibold ${PRIORITY_STYLES[card.priority] ?? PRIORITY_STYLES.Low}`}>
                        {card.priority} Priority
                      </span>
                      <span className="text-xs text-muted-foreground">{card.category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-primary">{currency(card.uplift_potential)}</div>
                    <div className="text-[11px] uppercase tracking-wider text-muted-foreground">uplift potential</div>
                  </div>
                </div>

                <div className="rounded-xl border border-primary/20 bg-primary/8 px-3 py-2 text-sm text-primary">
                  {card.cm_gap_description}
                </div>

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-xl border border-border bg-background p-3">
                    <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Current</div>
                    <div className="mt-1 text-2xl font-bold text-foreground">{currency(card.current_price)}</div>
                    <div className="text-xs text-muted-foreground">{card.current_cm_pct.toFixed(1)}% CM</div>
                  </div>
                  <div className="rounded-xl border border-success/20 bg-success/10 p-3">
                    <div className="text-[11px] uppercase tracking-wider text-success">Suggested</div>
                    <div className="mt-1 text-2xl font-bold text-success">{currency(card.suggested_price)}</div>
                    <div className="text-xs text-success">{card.target_cm_pct.toFixed(1)}% target</div>
                  </div>
                  <div className="rounded-xl border border-warning/20 bg-warning/10 p-3">
                    <div className="text-[11px] uppercase tracking-wider text-warning">Delta</div>
                    <div className="mt-1 text-2xl font-bold text-warning">+{currency(card.delta_amount)}</div>
                    <div className="text-xs text-warning">+{card.delta_pct.toFixed(0)}%</div>
                  </div>
                </div>

                <div className="text-sm text-muted-foreground">
                  Vol: <span className="font-semibold text-foreground">{card.volume_total}</span>
                  <span className="mx-2">·</span>
                  <span className="font-semibold text-foreground">{card.volume_per_day.toFixed(1)}/day</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}