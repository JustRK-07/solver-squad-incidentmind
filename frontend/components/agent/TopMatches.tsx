"use client";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { RecallHit } from "@/types/incident";

export interface TopMatchesProps {
  hits: RecallHit[];
  /** When a row is clicked — used to jump to the memory bank. */
  onSelect?: (id: string) => void;
}

/**
 * A compact "Top matches" widget shown above the recommendation card.
 * Pulls the top 3 recall hits out of the Agent tab and surfaces them
 * where judges actually look.
 */
export function TopMatches({ hits, onSelect }: TopMatchesProps) {
  const top = hits.slice(0, 3);
  if (top.length === 0) return null;

  return (
    <Card aria-label="top matches">
      <div className="flex items-center gap-2 mb-2">
        <h2 className="text-[15px] font-medium m-0">
          Top matches from Hindsight memory
        </h2>
        <Badge variant="default">{hits.length} total</Badge>
      </div>
      <div className="grid gap-1">
        {top.map((h, i) => (
          <button
            key={h.id}
            type="button"
            onClick={() => onSelect?.(h.id)}
            className="w-full grid grid-cols-[40px_1fr_auto_auto] gap-3 items-center px-2.5 py-2 rounded-md hover:bg-surface-muted text-left"
          >
            <span
              className={`text-[15px] font-medium tabular-nums ${
                h.sim >= 80 ? "text-success-fg" : h.sim >= 50 ? "text-info" : "text-muted-foreground"
              }`}
            >
              {h.sim}%
            </span>
            <div>
              <div className="text-[13px] font-medium">
                {h.id} <span className="text-muted-foreground font-normal">· {h.title}</span>
              </div>
            </div>
            <Badge
              variant={h.status === "resolved" ? "success" : "danger"}
            >
              {h.status}
            </Badge>
            <span className="text-[12px] text-muted-foreground tabular-nums">
              {h.mttr}
            </span>
            {i === 0 && (
              <span className="col-span-full text-[11px] text-info -mt-0.5">
                ★ best match · being used as the recommended fix
              </span>
            )}
          </button>
        ))}
      </div>
    </Card>
  );
}
