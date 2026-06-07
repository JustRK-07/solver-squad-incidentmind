"use client";

import { Lightbulb } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { Scenario } from "@/types/incident";

export interface HypothesisStripProps {
  scenario: Scenario;
}

/**
 * A one-line "Hypothesis" strip that sits directly under the incident
 * header. Calls out the predicted root cause, the confidence, and the
 * number of past incidents that cite this hypothesis.
 */
export function HypothesisStrip({ scenario }: HypothesisStripProps) {
  const tone = scenario.confidenceBand;
  const variant =
    tone === "high" ? "success" : tone === "medium" ? "warning" : "danger";
  return (
    <Card className="bg-info/[0.04] border-info/30">
      <div className="flex items-start gap-2">
        <Lightbulb className="h-3.5 w-3.5 text-info mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] text-muted-foreground uppercase tracking-wider">
              Hypothesis
            </span>
            <Badge variant={variant}>
              {scenario.confidence}% confidence · {tone}
            </Badge>
            <Badge variant="default">
              {scenario.citations.length} past incident
              {scenario.citations.length === 1 ? "" : "s"} cite this
            </Badge>
          </div>
          <p className="text-[14px] m-0 mt-1.5">{scenario.rootCause}</p>
        </div>
      </div>
    </Card>
  );
}
