"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkline } from "@/components/shared/Sparkline";
import type { TopMatch, ScenarioHistory } from "@/types/incident";

export interface WhyMatchedProps {
  top: TopMatch;
  history: ScenarioHistory;
}

type WhyTab = "rc" | "res" | "hist";

export function WhyMatched({ top, history }: WhyMatchedProps) {
  const [tab, setTab] = useState<WhyTab>("rc");
  return (
    <Card cream aria-label="why this matched" className="mt-1">
      <div className="flex items-center gap-2.5 mb-2.5">
        <h2 className="text-[15px] font-medium m-0">
          {top.id} · why this matched
        </h2>
        <div className="flex-1" />
        <Badge variant="default">{top.sim}% similar</Badge>
      </div>
      <Tabs value={tab} onValueChange={(v) => setTab(v as WhyTab)}>
        <TabsList>
          <TabsTrigger value="rc">Root cause</TabsTrigger>
          <TabsTrigger value="res">Resolution</TabsTrigger>
          <TabsTrigger value="hist">History</TabsTrigger>
        </TabsList>
        <TabsContent value="rc" className="text-[13px] mt-2.5">
          <p className="m-0">
            <span className="text-muted-foreground">Root cause:</span> {top.rootCause}
          </p>
        </TabsContent>
        <TabsContent value="res" className="text-[13px] mt-2.5">
          <p className="m-0">
            <span className="text-muted-foreground">Resolution:</span> {top.resolution}{" "}
            <span className="text-muted-foreground text-xs">
              (Resolved in {top.mttr}.)
            </span>
          </p>
        </TabsContent>
        <TabsContent value="hist" className="text-[13px] mt-2.5">
          <p className="text-muted-foreground mb-1">
            MTTR trend (last {history.mttr.length} occurrence{history.mttr.length === 1 ? "" : "s"}):
          </p>
          <Sparkline values={history.mttr} labels={history.labels} />
        </TabsContent>
      </Tabs>
    </Card>
  );
}
