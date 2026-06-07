"use client";

import { Download } from "lucide-react";

import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { Scenario, Step } from "@/types/incident";

export interface RecommendationCardProps {
  scenario: Scenario;
  onDownload: () => void;
}

export function RecommendationCard({ scenario, onDownload }: RecommendationCardProps) {
  return (
    <Card accent aria-label="recommendation" className="mt-1">
      {/* header */}
      <div className="flex items-center gap-2.5 mb-2.5">
        <span aria-hidden="true" className="inline-block w-3.5 text-muted-foreground text-center">
          ▢
        </span>
        <h2 className="text-[15px] font-medium m-0">Recommended remediation</h2>
        <div className="flex-1" />
        <div className="flex items-center gap-1.5">
          <Badge variant="muted">
            based on {scenario.citations.length} past incidents
          </Badge>
          <Button variant="ghost" size="sm" onClick={onDownload}>
            <Download className="h-3.5 w-3.5" />
            Download (JSON)
          </Button>
        </div>
      </div>

      {/* banners (only one shows at a time) */}
      {scenario.freshnessWarning && (
        <Alert variant="warning">⚠ {scenario.freshnessWarning}</Alert>
      )}
      {!scenario.verified && (
        <Alert variant="danger">
          ⚠ No prior incident — treating as novel, UNVERIFIED.
        </Alert>
      )}

      {/* steps */}
      <div className="grid gap-2">
        {(scenario.steps ?? []).map((s) => (
          <StepRow key={s.order} step={s} />
        ))}
      </div>
    </Card>
  );
}

function StepRow({ step }: { step: Step }) {
  const hasSources = step.sources && step.sources.length > 0;
  return (
    <div className="grid grid-cols-[1fr_auto] gap-3 items-start">
      <div className="text-[14px]">
        <span className="text-text font-normal">{step.order} · </span>
        {step.text}
      </div>
      {hasSources ? (
        <Badge variant="default">from {step.sources.join(" · ")}</Badge>
      ) : (
        <Badge variant="muted" className="opacity-50">
          no citation
        </Badge>
      )}
    </div>
  );
}
