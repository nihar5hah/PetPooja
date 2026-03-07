"use client";

import { motion } from "framer-motion";

import { Card, CardContent } from "@/components/ui/card";
import type { StrategyCard } from "@/lib/types";

function currency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function HiddenGemsTab({ cards }: { cards: StrategyCard[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
      {cards.map((card, index) => (
        <motion.div
          key={card.item_name}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.03 }}
        >
          <Card className="h-full border-violet-500/30 bg-card/95">
            <CardContent className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-bold text-foreground">{card.item_name}</h3>
                  <span className="mt-2 inline-flex rounded-md bg-violet-500/10 px-2 py-1 text-[11px] font-semibold text-violet-300">
                    {card.category}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-violet-300">{card.margin_pct.toFixed(1)}%</div>
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">margin</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="rounded-xl border border-violet-500/20 bg-violet-500/10 p-3">
                  <div className="text-2xl font-bold text-violet-200">{card.units}</div>
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Units</div>
                </div>
                <div className="rounded-xl border border-violet-500/20 bg-violet-500/10 p-3">
                  <div className="text-2xl font-bold text-violet-200">{currency(card.revenue)}</div>
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Revenue</div>
                </div>
                <div className="rounded-xl border border-violet-500/20 bg-violet-500/10 p-3">
                  <div className="text-2xl font-bold text-violet-200">{currency(card.profit)}</div>
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Profit</div>
                </div>
              </div>

              <div>
                <div className="mb-2 text-sm font-semibold text-primary">Recommended Actions</div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  {card.recommended_actions.map((action) => (
                    <div key={action} className="rounded-lg border border-border bg-background px-3 py-2">
                      {action}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}