"use client";

import { startTransition, useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";

export function useRealtimeRefresh(tables: string[], debounceMs = 800): number {
  const [refreshKey, setRefreshKey] = useState(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tableKey = tables.join(",");
  const tableList = tableKey ? tableKey.split(",") : [];

  useEffect(() => {
    const client = supabase;
    if (!client || tableList.length === 0) {
      return undefined;
    }

    const channel = client.channel(`dashboard-refresh:${tableKey}`);

    for (const table of tableList) {
      channel.on(
        "postgres_changes",
        { event: "*", schema: "public", table },
        () => {
          if (timerRef.current) {
            clearTimeout(timerRef.current);
          }
          timerRef.current = setTimeout(() => {
            startTransition(() => {
              setRefreshKey((current) => current + 1);
            });
          }, debounceMs);
        },
      );
    }

    channel.subscribe();

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      void client.removeChannel(channel);
    };
  }, [debounceMs, tableKey]);

  return refreshKey;
}