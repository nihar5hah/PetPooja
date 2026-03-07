"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, RefreshCw, FileUp } from "lucide-react";
import { uploadPosCsv, recomputeAnalytics } from "@/lib/api";
import type { IngestionResponse, RecomputeResponse, RecomputeParams } from "@/lib/types";
import { PageHeader } from "@/components/ui/page-header";
import { useToast } from "@/components/ui/toast";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { AnimatedPage } from "@/components/ui/data-display";

export default function OperationsPage() {
  const { toast } = useToast();

  /* CSV Upload */
  const [dragover, setDragover] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<IngestionResponse | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  /* Recompute */
  const [params, setParams] = useState<RecomputeParams>({
    min_support: 0.001,
    min_confidence: 0.15,
    min_lift: 1.0,
    max_rules: 200,
  });
  const [computing, setComputing] = useState(false);
  const [computeResult, setComputeResult] = useState<RecomputeResponse | null>(null);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      toast("Please upload a CSV file", "error");
      return;
    }
    setUploading(true);
    setUploadResult(null);
    try {
      const res = await uploadPosCsv(file);
      setUploadResult(res);
      toast(`Ingested ${res.rows_inserted} of ${res.rows_received} rows`, "success");
    } catch (e) {
      toast(e instanceof Error ? e.message : "Upload failed", "error");
    } finally {
      setUploading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragover(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function onFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  async function handleRecompute() {
    setComputing(true);
    setComputeResult(null);
    try {
      const res = await recomputeAnalytics(params);
      setComputeResult(res);
      toast(`Generated ${res.combo_rules_generated} combo rules`, "success");
    } catch (e) {
      toast(e instanceof Error ? e.message : "Recompute failed", "error");
    } finally {
      setComputing(false);
    }
  }

  function updateParam(key: keyof RecomputeParams, value: string) {
    const num = parseFloat(value);
    if (!isNaN(num)) setParams((p) => ({ ...p, [key]: num }));
  }

  return (
    <AnimatedPage>
      <PageHeader title="Operations" description="Data ingestion and analytics configuration" />

      {/* CSV Upload */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="size-4 text-primary" />
            Upload POS Transactions (CSV)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`group relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
              dragover
                ? "border-primary bg-primary/5"
                : "border-border hover:border-primary/60 hover:bg-muted/50"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragover(true);
            }}
            onDragLeave={() => setDragover(false)}
            onDrop={onDrop}
            onClick={() => fileRef.current?.click()}
          >
            <FileUp className="size-8 mx-auto mb-3 text-muted-foreground group-hover:text-primary transition-colors" />
            <p className="text-sm text-muted-foreground">
              {uploading ? "Uploading…" : "Drop CSV here or click to browse"}
            </p>
          </div>
          <input ref={fileRef} type="file" accept=".csv" onChange={onFileSelect} className="hidden" />

          {uploadResult && (
            <div className="mt-4 rounded-lg border border-border bg-muted/50 p-4">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Ingestion Result</h4>
              <pre className="text-xs text-foreground overflow-x-auto">{JSON.stringify(uploadResult, null, 2)}</pre>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recompute Analytics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="size-4 text-primary" />
            Recompute Analytics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Re-run menu engineering + association rule mining with custom thresholds.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <Label>Min Support</Label>
              <Input
                type="number"
                step="0.0001"
                min="0.0001"
                max="1"
                value={params.min_support}
                onChange={(e) => updateParam("min_support", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Min Confidence</Label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                value={params.min_confidence}
                onChange={(e) => updateParam("min_confidence", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Min Lift</Label>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={params.min_lift}
                onChange={(e) => updateParam("min_lift", e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Max Rules</Label>
              <Input
                type="number"
                step="1"
                min="1"
                max="1000"
                value={params.max_rules}
                onChange={(e) => updateParam("max_rules", e.target.value)}
              />
            </div>
          </div>

          <Button onClick={handleRecompute} disabled={computing} className="mt-4">
            <RefreshCw className={`size-3.5 mr-1.5 ${computing ? "animate-spin" : ""}`} />
            {computing ? "Computing…" : "Recompute Analytics"}
          </Button>

          {computeResult && (
            <div className="mt-4 rounded-lg border border-border bg-muted/50 p-4">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Recompute Result</h4>
              <pre className="text-xs text-foreground overflow-x-auto">{JSON.stringify(computeResult, null, 2)}</pre>
            </div>
          )}
        </CardContent>
      </Card>
    </AnimatedPage>
  );
}
