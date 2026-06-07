"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export interface OutcomeFormProps {
  defaultFix: string;
  defaultMttr: number;
  /** Fires when Worked/Failed is pressed. */
  onRecord: (outcome: "success" | "failure", fix: string, mttrMins: number) => void;
}

export function OutcomeForm({ defaultFix, defaultMttr, onRecord }: OutcomeFormProps) {
  const [fix, setFix] = useState(defaultFix);
  const [mttr, setMttr] = useState<string>(String(defaultMttr));

  // Re-prefill when a new diagnosis lands
  useEffect(() => {
    setFix(defaultFix);
    setMttr(String(defaultMttr));
  }, [defaultFix, defaultMttr]);

  const submit = (outcome: "success" | "failure") => {
    onRecord(outcome, fix.trim() || "(unspecified)", Number(mttr) || 0);
  };

  return (
    <Card aria-label="record outcome" className="mt-1">
      <h2 className="text-[15px] font-medium mb-2">
        Record outcome{" "}
        <span className="text-xs text-muted-foreground">— closes the learning loop</span>
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-[1fr_140px_auto_auto] gap-2 items-center">
        <Input
          value={fix}
          onChange={(e) => setFix(e.target.value)}
          placeholder="Fix you applied"
          aria-label="Fix you applied"
        />
        <Input
          type="number"
          min={1}
          value={mttr}
          onChange={(e) => setMttr(e.target.value)}
          placeholder="MTTR (min)"
          aria-label="MTTR (min)"
        />
        <Button
          type="button"
          variant="success"
          size="default"
          onClick={() => submit("success")}
        >
          ✓ Worked
        </Button>
        <Button
          type="button"
          variant="destructive"
          size="default"
          onClick={() => submit("failure")}
        >
          ✗ Failed
        </Button>
      </div>
    </Card>
  );
}
