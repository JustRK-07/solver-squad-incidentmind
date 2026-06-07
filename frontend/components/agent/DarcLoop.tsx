"use client";

import { Fragment } from "react";
import {
  Stethoscope,
  PlayCircle,
  ClipboardCheck,
  Database,
  Check,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export type DarcStep = "diagnose" | "act" | "record" | "consolidate";
export type DarcState = "pending" | "active" | "done";

export interface DarcLoopProps {
  /** Per-step state. */
  diagnose: DarcState;
  act: DarcState;
  record: DarcState;
  consolidate: DarcState;
}

interface StepDef {
  key: DarcStep;
  name: string;
  desc: string;
  Icon: typeof Stethoscope;
}

const STEPS: StepDef[] = [
  {
    key: "diagnose",
    name: "Diagnose",
    desc: "Recall similar past incidents",
    Icon: Stethoscope,
  },
  {
    key: "act",
    name: "Act",
    desc: "Apply the cited recommendation",
    Icon: PlayCircle,
  },
  {
    key: "record",
    name: "Record",
    desc: "Capture what fix was applied",
    Icon: ClipboardCheck,
  },
  {
    key: "consolidate",
    name: "Consolidate",
    desc: "Write outcome back to memory",
    Icon: Database,
  },
];

/**
 * The DARC loop visualised — Diagnose → Act → Record → Consolidate.
 * Lives at the bottom of the page so judges can see *exactly* where the
 * agent is in the loop and what closing the loop means. Each step lights
 * up as the user advances through the workflow.
 */
export function DarcLoop({ diagnose, act, record, consolidate }: DarcLoopProps) {
  const states: Record<DarcStep, DarcState> = { diagnose, act, record, consolidate };
  const doneCount = STEPS.filter((s) => states[s.key] === "done").length;

  return (
    <Card aria-label="DARC loop">
      <div className="flex items-center gap-2 mb-2.5">
        <h2 className="text-[15px] font-medium m-0">DARC loop</h2>
        <span className="text-xs text-muted-foreground">
          · Diagnose → Act → Record → Consolidate · {doneCount}/4 complete
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-[1fr_12px_1fr_12px_1fr_12px_1fr] gap-2 items-stretch">
        {STEPS.map((s, i) => (
          <Fragment key={s.key}>
            <Step step={s} state={states[s.key]} />
            {i < STEPS.length - 1 && (
              <Connector active={states[s.key] === "done"} />
            )}
          </Fragment>
        ))}
      </div>
    </Card>
  );
}

function Step({ step, state }: { step: StepDef; state: DarcState }) {
  const { Icon } = step;
  const tone =
    state === "done"
      ? "bg-success-bg border-success-fg text-success-fg"
      : state === "active"
        ? "bg-info/[0.06] border-info text-info"
        : "border-border text-muted-foreground";
  return (
    <div
      className={cn(
        "rounded-md border-hairline p-2.5 grid gap-1",
        tone,
      )}
    >
      <div className="flex items-center gap-1.5">
        {state === "done" ? (
          <Check className="h-3.5 w-3.5" />
        ) : (
          <Icon className="h-3.5 w-3.5" />
        )}
        <span className="text-[13px] font-medium">{step.name}</span>
        {state === "active" && (
          <span className="ml-auto text-[10px] uppercase tracking-wider">
            in progress
          </span>
        )}
        {state === "done" && (
          <span className="ml-auto text-[10px] uppercase tracking-wider">
            done
          </span>
        )}
      </div>
      <div className="text-[11px] opacity-80">{step.desc}</div>
    </div>
  );
}

function Connector({ active }: { active: boolean }) {
  return (
    <div className="hidden md:flex items-center justify-center">
      <div
        className={cn(
          "h-px w-full",
          active ? "bg-success-fg" : "bg-border",
        )}
      />
    </div>
  );
}
