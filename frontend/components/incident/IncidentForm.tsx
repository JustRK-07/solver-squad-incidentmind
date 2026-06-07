"use client";

import { useState } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface IncidentFormProps {
  service: string;
  symptom: string;
  useMemory: boolean;
  isRunning: boolean;
  onServiceChange: (s: string) => void;
  onSymptomChange: (s: string) => void;
  onUseMemoryChange: (v: boolean) => void;
  onSubmit: () => void;
}

export function IncidentForm({
  service,
  symptom,
  useMemory,
  isRunning,
  onServiceChange,
  onSymptomChange,
  onUseMemoryChange,
  onSubmit,
}: IncidentFormProps) {
  const [open, setOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!symptom.trim()) return;
    onSubmit();
  };

  return (
    <Collapsible
      open={open}
      onOpenChange={setOpen}
      className="rounded-lg border-hairline border-border bg-surface"
    >
      <CollapsibleTrigger className="flex items-center gap-1.5 w-full px-3.5 py-2.5 text-[13px] text-muted-foreground cursor-pointer select-none hover:text-text">
        <span
          aria-hidden="true"
          className={`text-muted-foreground transition-transform ${open ? "rotate-90" : ""}`}
        >
          ▸
        </span>
        Paste a custom symptom
      </CollapsibleTrigger>
      <CollapsibleContent>
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-[1fr_2fr_auto] gap-2 items-stretch px-3.5 pb-3.5 pt-3 border-t border-dashed border-border"
        >
          <Input
            value={service}
            onChange={(e) => onServiceChange(e.target.value)}
            placeholder="Service"
            aria-label="Service"
          />
          <Input
            value={symptom}
            onChange={(e) => onSymptomChange(e.target.value)}
            placeholder="Symptom"
            aria-label="Symptom"
          />
          <Button
            type="submit"
            variant="default"
            disabled={isRunning}
            className="whitespace-nowrap"
          >
            {isRunning ? "Diagnosing…" : "Diagnose"}
          </Button>

          {/* memory toggle row */}
          <div className="col-span-full flex items-center gap-3 flex-wrap">
            <label className="inline-flex items-center gap-1.5 text-[13px] cursor-pointer">
              <Checkbox
                checked={useMemory}
                onCheckedChange={(v) => onUseMemoryChange(Boolean(v))}
              />
              <span>
                Memory <strong>{useMemory ? "ON" : "OFF"}</strong>
              </span>
            </label>
            <span
              className={`text-xs ${useMemory ? "text-muted-foreground" : "text-warning-fg"}`}
            >
              {useMemory
                ? "— recall from Hindsight, cite past incidents"
                : "— raw LLM, no recall, no citations"}
            </span>
          </div>
        </form>
      </CollapsibleContent>
    </Collapsible>
  );
}
