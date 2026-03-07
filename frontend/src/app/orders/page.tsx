"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ShoppingCart, IndianRupee, TrendingUp, AlertTriangle, RotateCcw } from "lucide-react";
import { getOrders, getFailedOrders, retryFailedOrder } from "@/lib/api";
import { useRealtimeRefresh } from "@/hooks/use-realtime-refresh";
import type { Order, FailedOrder } from "@/lib/types";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Tabs,
  SortableHeader,
  EmptyState,
  Spinner,
  AnimatedPage,
} from "@/components/ui/data-display";

type SortKey = keyof Order;
type SortDir = "asc" | "desc";

function currency(v: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(v);
}

export default function OrdersPage() {
  const { toast } = useToast();
  const refreshKey = useRealtimeRefresh(["orders", "failed_order_queue", "pos_transactions"], 1000);
  const [orders, setOrders] = useState<Order[]>([]);
  const [failed, setFailed] = useState<FailedOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("id");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [statusFilter, setStatusFilter] = useState("All");
  const [retrying, setRetrying] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([getOrders(), getFailedOrders()])
      .then(([o, f]) => {
        setOrders(o);
        setFailed(f);
      })
      .finally(() => setLoading(false));
  }, [refreshKey]);

  const statuses = useMemo(() => {
    const s = new Set(orders.map((o) => o.status));
    return ["All", ...Array.from(s)];
  }, [orders]);

  const filtered = useMemo(() => {
    let list = orders;
    if (statusFilter !== "All") list = list.filter((o) => o.status === statusFilter);
    const dir = sortDir === "asc" ? 1 : -1;
    return [...list].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string") return dir * av.localeCompare(bv as string);
      return dir * ((av as number) - (bv as number));
    });
  }, [orders, statusFilter, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  async function handleRetry(id: number) {
    setRetrying(id);
    try {
      const res = await retryFailedOrder(id);
      toast(`Retry ${res.status} – order ${res.order_id ?? "pending"}`, "success");
      setFailed((prev) => prev.filter((f) => f.id !== id));
    } catch {
      toast("Retry failed", "error");
    } finally {
      setRetrying(null);
    }
  }

  const totalRev = orders.reduce((s, o) => s + o.total_amount, 0);
  const avgOrder = orders.length ? totalRev / orders.length : 0;

  if (loading) return <Spinner />;

  return (
    <AnimatedPage>
      <PageHeader title="Orders" description="Voice-placed orders and failed order queue" />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Orders" value={String(orders.length)} icon={<ShoppingCart className="size-4" />} />
        <StatCard label="Revenue" value={currency(totalRev)} icon={<IndianRupee className="size-4" />} />
        <StatCard label="Avg Order" value={currency(avgOrder)} icon={<TrendingUp className="size-4" />} />
        <StatCard label="Failed Queue" value={String(failed.length)} icon={<AlertTriangle className="size-4" />} />
      </div>

      {/* Status filter */}
      <div className="mb-4">
        <Tabs tabs={statuses} active={statusFilter} onChange={setStatusFilter} />
      </div>

      {/* Orders table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Recent Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <SortableHeader label="ID" active={sortKey === "id"} direction={sortDir} onClick={() => toggleSort("id")} />
                  <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Call ID</th>
                  <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Phone</th>
                  <SortableHeader label="Status" active={sortKey === "status"} direction={sortDir} onClick={() => toggleSort("status")} />
                  <SortableHeader label="Total" active={sortKey === "total_amount"} direction={sortDir} onClick={() => toggleSort("total_amount")} className="text-right" />
                  <SortableHeader label="Date" active={sortKey === "created_at"} direction={sortDir} onClick={() => toggleSort("created_at")} />
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((o, idx) => (
                  <motion.tr
                    key={o.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.02 }}
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <td className="px-3 py-2.5 text-xs font-medium">#{o.id}</td>
                    <td className="px-3 py-2.5 text-xs font-mono text-muted-foreground">{o.call_id}</td>
                    <td className="px-3 py-2.5 text-xs">{o.customer_phone || "—"}</td>
                    <td className="px-3 py-2.5"><StatusBadge value={o.status} /></td>
                    <td className="px-3 py-2.5 text-xs text-right tabular-nums">{currency(o.total_amount)}</td>
                    <td className="px-3 py-2.5 text-xs text-muted-foreground">{new Date(o.created_at).toLocaleDateString()}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && (
            <EmptyState
              icon={<ShoppingCart className="size-8" />}
              title="No orders"
              description="No voice orders have been placed yet."
            />
          )}
        </CardContent>
      </Card>

      {/* Failed orders */}
      {failed.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Failed Order Queue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">ID</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Call ID</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Reason</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Retries</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Status</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {failed.map((f) => (
                    <tr key={f.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-3 py-2.5 text-xs font-medium">#{f.id}</td>
                      <td className="px-3 py-2.5 text-xs font-mono text-muted-foreground">{f.call_id}</td>
                      <td className="px-3 py-2.5 text-xs">{f.failure_reason}</td>
                      <td className="px-3 py-2.5 text-xs tabular-nums">{f.retry_count}</td>
                      <td className="px-3 py-2.5"><StatusBadge value={f.status} /></td>
                      <td className="px-3 py-2.5">
                        <Button size="sm" disabled={retrying === f.id} onClick={() => handleRetry(f.id)}>
                          <RotateCcw className="size-3 mr-1" />
                          {retrying === f.id ? "Retrying…" : "Retry"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </AnimatedPage>
  );
}
