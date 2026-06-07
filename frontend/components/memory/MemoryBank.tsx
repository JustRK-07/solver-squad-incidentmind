"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Sparkline } from "@/components/shared/Sparkline";
import { cn } from "@/lib/utils";
import { BANK_INCIDENTS, INCIDENT_DETAIL } from "@/lib/mockData";
import type { BankIncident, Outcome } from "@/types/incident";

export interface MemoryBankProps {
  /** Initial selection (e.g. INC-231 for the open incident). */
  initialId?: string | null;
  /** Notifies parent when a row is selected (e.g. to highlight in the recall list). */
  onSelect?: (id: string) => void;
}

export function MemoryBank({ initialId, onSelect }: MemoryBankProps) {
  const [selectedId, setSelectedId] = useState<string | null>(initialId ?? null);
  const selected = BANK_INCIDENTS.find((b) => b.id === selectedId) ?? null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-[320px_1fr] gap-3 min-h-[320px]">
      {/* list */}
      <div className="rounded-lg border-hairline border-border bg-surface-muted max-h-[480px] overflow-auto">
        {BANK_INCIDENTS.map((inc) => (
          <BankRow
            key={inc.id}
            inc={inc}
            selected={inc.id === selectedId}
            onSelect={(id) => {
              setSelectedId(id);
              onSelect?.(id);
            }}
          />
        ))}
      </div>

      {/* detail */}
      <div className="grid gap-2.5 content-start">
        {selected ? (
          <BankDetail inc={selected} />
        ) : (
          <p className="text-sm text-muted-foreground">
            Select an incident from the list to inspect it.
          </p>
        )}
      </div>
    </div>
  );
}

function BankRow({
  inc,
  selected,
  onSelect,
}: {
  inc: BankIncident;
  selected: boolean;
  onSelect: (id: string) => void;
}) {
  const mttrLabel = inc.mttr ? `${inc.mttr}m` : "—";
  return (
    <button
      type="button"
      onClick={() => onSelect(inc.id)}
      className={cn(
        "w-full text-left grid grid-cols-[1fr_auto] gap-1.5 px-3 py-2.5 border-b border-hairline border-border last:border-b-0 hover:bg-black/[0.03] cursor-pointer",
        selected && "bg-info/[0.08] border-l-[3px] border-l-info pl-2.5",
      )}
    >
      <div>
        <div className="font-medium text-[13px] flex items-center gap-1.5">
          {inc.id}
          {inc.freshness === "weakening" && <Badge variant="warning">weakening</Badge>}
        </div>
        <div className="text-xs text-muted-foreground mt-0.5">
          {inc.svc} · {inc.title}
        </div>
      </div>
      <div className="text-right text-[11px] text-muted-foreground">
        <OutcomePill outcome={inc.outcome} />
        <br />
        <span>{inc.date} · {mttrLabel}</span>
      </div>
    </button>
  );
}

function OutcomePill({ outcome }: { outcome: Outcome }) {
  if (outcome === "success") return <Badge variant="success">success</Badge>;
  if (outcome === "failure") return <Badge variant="danger">failure</Badge>;
  return <Badge variant="warning">open</Badge>;
}

function BankDetail({ inc }: { inc: BankIncident }) {
  const det = INCIDENT_DETAIL[inc.id] ?? {
    rootCause: "—",
    resolution: "—",
    mttr: null,
    fix: "—",
    date: inc.date,
    tags: [],
  };
  // a tiny trend for the bank detail: pull this incident's history if present
  const trend = histFor(inc.id);
  return (
    <>
      <Card>
        <div className="flex items-baseline gap-2.5">
          <h2 className="text-base font-medium m-0">{inc.id}</h2>
          {inc.freshness === "weakening" && <Badge variant="warning">weakening</Badge>}
          <OutcomePill outcome={inc.outcome} />
          <Badge variant="neutral">{inc.mttr ? `${inc.mttr}m` : "open"}</Badge>
        </div>
        <h3 className="text-xs font-medium text-muted-foreground mt-2">
          {inc.svc} · {inc.title}
        </h3>
        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2">
          <Field k="Date" v={det.date ?? inc.date} />
          <Field k="MTTR" v={inc.mttr ? `${inc.mttr}m` : "—"} />
          <Field k="Status" v={inc.status} />
          <Field k="Outcome" v={inc.outcome} />
        </div>
        {trend.mttr.length > 1 && (
          <div className="mt-3 pt-3 border-t border-dashed border-border">
            <h3 className="text-xs font-medium text-muted-foreground mb-1">MTTR trend</h3>
            <Sparkline values={trend.mttr} labels={trend.labels} />
          </div>
        )}
      </Card>

      <Card>
        <h3 className="text-xs font-medium text-muted-foreground m-0">Root cause</h3>
        <p className="mt-1 mb-0">{det.rootCause}</p>
      </Card>

      <Card>
        <h3 className="text-xs font-medium text-muted-foreground m-0">Resolution</h3>
        <p className="mt-1 mb-0">
          <strong>Fix:</strong> {det.fix}
        </p>
        <p className="mt-1.5 mb-0">
          <strong>Outcome:</strong> {det.resolution}
        </p>
      </Card>

      {det.tags.length > 0 && (
        <Card cream>
          <h3 className="text-xs font-medium text-muted-foreground m-0">Tags</h3>
          <div className="flex items-center gap-1.5 flex-wrap mt-1.5">
            {det.tags.map((t) => (
              <Badge key={t}>{t}</Badge>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}

function Field({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <div className="text-[11px] text-muted-foreground">{k}</div>
      <div className="text-[13px] font-medium">{v}</div>
    </div>
  );
}

/** Tiny lookup: derive a per-bank-incident MTTR trend from a few known cases. */
function histFor(id: string): { mttr: number[]; labels: string[] } {
  const map: Record<string, { mttr: number[]; labels: string[] }> = {
    "INC-204": { mttr: [125, 72, 52, 38], labels: ["INC-093", "INC-187", "INC-119", "INC-204"] },
    "INC-005": { mttr: [60, 130, 90], labels: ["INC-005", "INC-009", "INC-010"] },
    "INC-004": { mttr: [60, 110], labels: ["INC-003", "INC-004"] },
  };
  return map[id] ?? { mttr: [], labels: [] };
}
