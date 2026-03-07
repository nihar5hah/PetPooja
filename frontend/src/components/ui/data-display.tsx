"use client";

import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { useState, type ReactNode } from "react";

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: string[];
  active: string;
  onChange: (tab: string) => void;
}) {
  return (
    <div className="flex items-center gap-0.5 rounded-lg border border-border bg-muted p-0.5">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={cn(
            "relative rounded-md px-3 py-1.5 text-xs font-medium transition-colors cursor-pointer",
            active === tab
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {active === tab && (
            <motion.div
              layoutId="tab-active"
              className="absolute inset-0 rounded-md bg-background border border-border shadow-sm"
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative">{tab}</span>
        </button>
      ))}
    </div>
  );
}

export function DataTable({
  headers,
  children,
  className,
}: {
  headers: { label: string; sortKey?: string; className?: string }[];
  children: ReactNode;
  className?: string;
  onSort?: (key: string) => void;
  sortKey?: string;
  sortDir?: "asc" | "desc";
}) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {headers.map((h, i) => (
              <th
                key={i}
                className={cn(
                  "px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground",
                  h.className,
                )}
              >
                {h.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">{children}</tbody>
      </table>
    </div>
  );
}

export function SortableHeader({
  label,
  active,
  direction,
  onClick,
  className,
}: {
  label: string;
  active: boolean;
  direction: "asc" | "desc";
  onClick: () => void;
  className?: string;
}) {
  return (
    <th
      onClick={onClick}
      className={cn(
        "cursor-pointer select-none px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors",
        active && "text-foreground",
        className,
      )}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        {active && (
          <span className="text-primary text-[10px]">
            {direction === "asc" ? "▲" : "▼"}
          </span>
        )}
      </span>
    </th>
  );
}

export function EmptyState({
  icon,
  title,
  description,
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-3 text-muted-foreground/40">{icon}</div>
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1 text-xs text-muted-foreground max-w-xs">{description}</p>
    </div>
  );
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 rounded-full bg-muted overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="h-full rounded-full bg-primary"
        />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground">{pct}%</span>
    </div>
  );
}

export function Spinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="size-6 animate-spin rounded-full border-2 border-muted-foreground/20 border-t-primary" />
    </div>
  );
}

export function AnimatedPage({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}
