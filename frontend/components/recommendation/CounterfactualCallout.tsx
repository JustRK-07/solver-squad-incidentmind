"use client";

import { GitCompareArrows } from "lucide-react";

import { Card } from "@/components/ui/card";
import { MTTR_BASELINE_MINS } from "@/lib/mockData";
import type { Scenario } from "@/types/incident";

export interface CounterfactualCalloutProps {
  scenario: Scenario;
}

/**
 * The "what if we didn't have memory" counterfactual — a 1-line callout
 * shown directly under the recommendation. Converts the abstract
 * `~38m` into a concrete "this would have been 6× slower without us."
 */
export function CounterfactualCallout({ scenario }: CounterfactualCalloutProps) {
  const without = MTTR_BASELINE_MINS;
  const withMttr = scenario.mttr;
  const speedup = without / Math.max(1, withMttr);
  const speedupLabel = speedup >= 10
    ? `${Math.round(speedup)}×`
    : `${speedup.toFixed(1)}×`;
  return (
    <Card className="bg-surface-muted">
      <div className="flex items-start gap-2 text-[13px]">
        <GitCompareArrows className="h-3.5 w-3.5 text-muted-foreground mt-0.5 shrink-0" />
        <p className="m-0">
          <strong>Without Hindsight memory</strong> this incident would
          default to the generic {without}m baseline. The {withMttr}m
          estimate is grounded in {scenario.retrieved.length} past case
          {scenario.retrieved.length === 1 ? "" : "s"} —{" "}
          <span className="text-info font-medium">
            {speedupLabel} faster
          </span>
          .
        </p>
      </div>
    </Card>
  );
}
