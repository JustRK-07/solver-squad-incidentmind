"use client";

import { Button } from "@/components/ui/button";

export interface QuickAction {
  label: string;
  emoji: string;
  symptom: string;
  service: string;
}

export const QUICK_ACTIONS: QuickAction[] = [
  {
    label: "Login 429 cascade",
    emoji: "⚡",
    symptom: "Login 429 cascade during a traffic surge; clients see ERR_TOO_MANY_REQUESTS",
    service: "Auth Service",
  },
  {
    label: "OOMKilled worker",
    emoji: "💥",
    symptom: "Worker pods OOMKilled in a loop; job queue backing up",
    service: "Recommendation Worker",
  },
  {
    label: "5xx after deploy",
    emoji: "📉",
    symptom: "5xx spike after deploy 7f3ac1; p99 latency 6.2s; DB connections pinned at 100/100",
    service: "payments-api-prod",
  },
  {
    label: "TLS cert expiry",
    emoji: "🔒",
    symptom: "HTTPS requests failing with SSL handshake errors across every service",
    service: "API Gateway",
  },
  {
    label: "Stale read replica",
    emoji: "🕒",
    symptom: "Stale order status right after placing an order; read replica lag at 12s",
    service: "Orders API",
  },
];

export interface QuickActionsProps {
  /** Fires when a chip is clicked. Use to drive the diagnose pipeline. */
  onPick: (symptom: string, service: string) => void;
}

export function QuickActions({ onPick }: QuickActionsProps) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-xs text-muted-foreground mr-1">Try:</span>
      {QUICK_ACTIONS.map((qa) => (
        <Button
          key={qa.label}
          variant="outline"
          size="sm"
          onClick={() => onPick(qa.symptom, qa.service)}
        >
          <span aria-hidden="true">{qa.emoji}</span>
          {qa.label}
        </Button>
      ))}
    </div>
  );
}
