"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Mic2, Send, RotateCcw, Phone } from "lucide-react";
import { processVoiceOrder, getVoiceCallLogs } from "@/lib/api";
import type { VoiceWebhookPayload, VoiceWebhookResponse, VoiceCallLog } from "@/lib/types";
import { PageHeader } from "@/components/ui/page-header";
import { StatusBadge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Textarea, Label } from "@/components/ui/input";
import { EmptyState, Spinner, AnimatedPage } from "@/components/ui/data-display";

function emptyPayload(): VoiceWebhookPayload {
  return {
    call_id: `sim_${Date.now()}`,
    customer_phone: "",
    transcript: "",
    ordered_items: [],
    confirm_order: false,
  };
}

export default function VoiceLabPage() {
  const { toast } = useToast();
  const [payload, setPayload] = useState<VoiceWebhookPayload>(emptyPayload);
  const [itemsText, setItemsText] = useState("");
  const [sending, setSending] = useState(false);
  const [response, setResponse] = useState<VoiceWebhookResponse | null>(null);
  const [logs, setLogs] = useState<VoiceCallLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(true);

  useEffect(() => {
    getVoiceCallLogs()
      .then(setLogs)
      .finally(() => setLogsLoading(false));
  }, []);

  const parseItems = useCallback((text: string) => {
    setItemsText(text);
    const items = text
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const match = line.match(/^(\d+)\s*x?\s+(.+)$/i) || line.match(/^(.+?)\s*x?\s*(\d+)$/i);
        if (match) {
          const first = match[1];
          const second = match[2];
          if (/^\d+$/.test(first)) return { item_name: second.trim(), quantity: parseInt(first) };
          return { item_name: first.trim(), quantity: parseInt(second) };
        }
        return { item_name: line, quantity: 1 };
      });
    setPayload((p) => ({ ...p, ordered_items: items }));
  }, []);

  async function handleSubmit() {
    if (!payload.ordered_items?.length && !payload.transcript) {
      toast("Add items or a transcript", "error");
      return;
    }
    setSending(true);
    try {
      const res = await processVoiceOrder(payload);
      setResponse(res);
      toast(`Voice order ${res.status}`, res.status === "error" ? "error" : "success");
      getVoiceCallLogs().then(setLogs);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Request failed", "error");
    } finally {
      setSending(false);
    }
  }

  function resetForm() {
    setPayload(emptyPayload());
    setItemsText("");
    setResponse(null);
  }

  return (
    <AnimatedPage>
      <PageHeader title="Voice Lab" description="Simulate voice orders and view call logs" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic2 className="size-4 text-primary" />
              Voice Order Simulator
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>Call ID</Label>
              <Input
                value={payload.call_id}
                onChange={(e) => setPayload((p) => ({ ...p, call_id: e.target.value }))}
              />
            </div>

            <div className="space-y-1.5">
              <Label>Customer Phone</Label>
              <Input
                value={payload.customer_phone}
                onChange={(e) => setPayload((p) => ({ ...p, customer_phone: e.target.value }))}
                placeholder="+91…"
              />
            </div>

            <div className="space-y-1.5">
              <Label>Transcript</Label>
              <Textarea
                rows={3}
                value={payload.transcript}
                onChange={(e) => setPayload((p) => ({ ...p, transcript: e.target.value }))}
                placeholder="I'd like to order two butter naans and a paneer tikka…"
              />
            </div>

            <div className="space-y-1.5">
              <Label>Items (one per line, e.g. &quot;2 Butter Naan&quot;)</Label>
              <Textarea
                rows={4}
                value={itemsText}
                onChange={(e) => parseItems(e.target.value)}
                placeholder={"2 Butter Naan\n1 Paneer Tikka\n3 Dal Makhani"}
              />
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={payload.confirm_order ?? false}
                onChange={(e) => setPayload((p) => ({ ...p, confirm_order: e.target.checked }))}
                className="rounded border-border accent-primary"
              />
              <span className="text-sm">Confirm order immediately</span>
            </label>

            <div className="flex gap-2 pt-1">
              <Button onClick={handleSubmit} disabled={sending}>
                <Send className="size-3.5 mr-1.5" />
                {sending ? "Sending…" : "Send Voice Order"}
              </Button>
              <Button variant="secondary" onClick={resetForm}>
                <RotateCcw className="size-3.5 mr-1.5" />
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Response */}
        <Card>
          <CardHeader>
            <CardTitle>Response</CardTitle>
          </CardHeader>
          <CardContent>
            {response ? (
              <div className="rounded-lg border border-border bg-muted/50 p-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                  Status: {response.status}
                </h4>
                <pre className="text-xs text-foreground overflow-x-auto">{JSON.stringify(response, null, 2)}</pre>
              </div>
            ) : (
              <EmptyState
                icon={<Mic2 className="size-8" />}
                title="No response yet"
                description="Submit a voice order to see the API response."
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Call logs */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="size-4 text-primary" />
            Voice Call Logs
          </CardTitle>
        </CardHeader>
        <CardContent>
          {logsLoading ? (
            <Spinner />
          ) : logs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">ID</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Call ID</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Outcome</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Transcript</th>
                    <th className="px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {logs.map((l, idx) => (
                    <motion.tr
                      key={l.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: idx * 0.03 }}
                      className="hover:bg-muted/50 transition-colors"
                    >
                      <td className="px-3 py-2.5 text-xs font-medium">#{l.id}</td>
                      <td className="px-3 py-2.5 text-xs font-mono text-muted-foreground">{l.call_id}</td>
                      <td className="px-3 py-2.5"><StatusBadge value={l.outcome} /></td>
                      <td className="px-3 py-2.5 text-xs text-muted-foreground max-w-[300px] truncate">
                        {l.transcript || "—"}
                      </td>
                      <td className="px-3 py-2.5 text-xs text-muted-foreground">{new Date(l.created_at).toLocaleDateString()}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              icon={<Phone className="size-8" />}
              title="No call logs"
              description="Voice call logs will appear here after processing orders."
            />
          )}
        </CardContent>
      </Card>
    </AnimatedPage>
  );
}
