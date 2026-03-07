"use client";

import { motion } from "framer-motion";

import { Card, CardContent } from "@/components/ui/card";
import type { UpsellCard } from "@/lib/types";

export function UpsellTab({ cards }: { cards: UpsellCard[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-4">
      {cards.map((card, index) => (
        <motion.div
          key={card.base_item}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.03 }}
        >
          <Card className="h-full border-primary/15 bg-card/95">
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-xl font-bold text-primary">{card.base_item}</h3>
                <span className="mt-2 inline-flex rounded-md bg-info/10 px-2 py-1 text-[11px] font-semibold text-info">
                  {card.category}
                </span>
              </div>

              <div className="space-y-2.5">
                {card.suggestions.map((suggestion) => (
                  <div key={`${card.base_item}-${suggestion.item_name}`} className="rounded-xl border border-border bg-background p-3">
                    <div className="flex items-start gap-3">
                      <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                        {suggestion.rank}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-semibold text-foreground">{suggestion.item_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {suggestion.category} · {suggestion.co_order_count}x co-ordered
                        </div>
                      </div>
                      <div className="rounded-md bg-success/10 px-2 py-1 text-xs font-semibold text-success">
                        {suggestion.margin_pct.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}