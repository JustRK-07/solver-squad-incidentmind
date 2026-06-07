"use client";

import { Activity } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { STATS } from "@/lib/stats";

/**
 * A small heatmap of services × incident count. Shows that memory
 * is tracking the *system*, not just one incident.
 */
export function ServiceHealth() {
  const max = Math.max(...STATS.services.map((s) => s.incidentCount), 1);

  return (
    <Card aria-label="service health">
      <div className="flex items-center gap-2 mb-2">
        <Activity className="h-3.5 w-3.5 text-muted-foreground" />
        <h2 className="text-[15px] font-medium m-0">Service health</h2>
        <span className="text-xs text-muted-foreground">
          · Hindsight monitors {STATS.services.length} services
        </span>
      </div>
      <div className="grid gap-1.5">
        {STATS.services.map((s) => {
          const intensity = s.incidentCount / max;
          const tone =
            s.openCount > 0
              ? "bg-danger-bg border-danger-fg text-danger-fg"
              : s.failureCount > 0
                ? "bg-warning-bg border-warning-fg text-warning-fg"
                : "bg-success-bg border-success-fg text-success-fg";
          return (
            <div
              key={s.service}
              className="grid grid-cols-[1fr_auto_auto] gap-3 items-center"
            >
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "inline-block w-2.5 h-2.5 rounded-full border-hairline",
                    tone,
                  )}
                  style={{ opacity: 0.3 + 0.7 * intensity }}
                />
                <span className="text-[13px] font-medium font-mono">{s.service}</span>
                <span className="text-[11px] text-muted-foreground">
                  {s.openCount > 0 && (
                    <span className="text-danger-fg mr-1.5">
                      {s.openCount} open
                    </span>
                  )}
                  {s.failureCount > 0 && (
                    <span className="text-warning-fg mr-1.5">
                      {s.failureCount} failure{s.failureCount === 1 ? "" : "s"}
                    </span>
                  )}
                </span>
              </div>
              <div className="text-[12px] text-muted-foreground tabular-nums">
                {s.incidentCount} incident{s.incidentCount === 1 ? "" : "s"}
              </div>
              <Badge
                variant={
                  s.fresh === "fresh" ? "danger" : s.fresh === "warm" ? "warning" : "muted"
                }
              >
                {s.fresh}
              </Badge>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
