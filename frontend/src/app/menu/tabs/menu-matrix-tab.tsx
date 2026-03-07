"use client";

import { motion } from "framer-motion";
import { Diamond, Eye, ShieldAlert, Star } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MenuMatrixView } from "@/lib/types";

const QUADRANT_STYLES: Record<string, { icon: typeof Star; border: string; chip: string; iconBox: string }> = {
  stars: {
    icon: Star,
    border: "border-amber-500/40",
    chip: "text-amber-300 border-amber-500/20 bg-amber-500/10",
    iconBox: "bg-amber-500/12 text-amber-300",
  },
  hidden_gems: {
    icon: Diamond,
    border: "border-violet-500/40",
    chip: "text-violet-200 border-violet-500/20 bg-violet-500/10",
    iconBox: "bg-violet-500/12 text-violet-300",
  },
  watch_list: {
    icon: Eye,
    border: "border-rose-500/40",
    chip: "text-rose-200 border-rose-500/20 bg-rose-500/10",
    iconBox: "bg-rose-500/12 text-rose-300",
  },
  laggards: {
    icon: ShieldAlert,
    border: "border-slate-500/40",
    chip: "text-slate-200 border-slate-500/20 bg-slate-500/10",
    iconBox: "bg-slate-500/12 text-slate-300",
  },
};

export function MenuMatrixTab({ data }: { data: MenuMatrixView }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <span className="rounded-full border border-border bg-card px-3 py-1.5">
          Median units threshold: <span className="font-semibold text-foreground">{data.units_median.toFixed(0)}</span>
        </span>
        <span className="rounded-full border border-border bg-card px-3 py-1.5">
          Median margin threshold: <span className="font-semibold text-foreground">{data.margin_median.toFixed(1)}%</span>
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        {data.quadrants.map((quadrant, index) => {
          const style = QUADRANT_STYLES[quadrant.key] ?? QUADRANT_STYLES.laggards;
          const Icon = style.icon;
          return (
            <motion.div
              key={quadrant.key}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className={`h-full bg-card/95 ${style.border}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className={`flex size-11 items-center justify-center rounded-xl ${style.iconBox}`}>
                      <Icon className="size-5" />
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold tracking-tight text-foreground">{quadrant.count}</div>
                      <div className="text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Items</div>
                    </div>
                  </div>
                  <CardTitle className="pt-2 text-lg font-bold text-foreground">{quadrant.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{quadrant.description}</p>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex flex-wrap gap-2">
                    {quadrant.items.map((item) => (
                      <div key={item.item_name} className={`rounded-lg border px-2.5 py-2 text-xs ${style.chip}`}>
                        <div className="font-medium text-foreground">{item.item_name}</div>
                        <div className="mt-0.5 text-[11px]">{item.margin_pct.toFixed(1)}% margin</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}