"use client";

import { Bell, Play, UserCircle2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export interface SiteHeaderProps {
  /** Play demo button label (updates per beat while the demo is running). */
  demoLabel?: string;
  /** Disable the Play demo button while a demo is in progress. */
  demoDisabled?: boolean;
  /** Click handler for the Play demo button. */
  onPlayDemo?: () => void;
}

export function SiteHeader({
  demoLabel = "▶ Play demo",
  demoDisabled = false,
  onPlayDemo,
}: SiteHeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex items-center gap-4 px-6 py-2.5 bg-surface border-b border-hairline border-border">
      {/* brand */}
      <div className="flex items-center gap-2.5">
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-md bg-primary text-primary-foreground text-[13px] font-semibold">
          IM
        </span>
        <span className="text-base font-medium">AfterMath</span>
        <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-warning-bg text-warning-fg uppercase tracking-wider">
          demo
        </span>
      </div>

      {/* middle: memory health + summary */}
      <div className="flex-1 flex items-center gap-3">
        <Badge variant="success" title="Hindsight memory layer">
          ● memory healthy
        </Badge>
        <span className="text-xs text-muted-foreground">
          — 12 incidents · 4 patterns
        </span>
      </div>

      {/* right: play demo + icons */}
      <div className="flex items-center gap-2.5">
        <Button
          variant="default"
          size="sm"
          onClick={onPlayDemo}
          disabled={demoDisabled}
          className="min-w-[140px] justify-center"
        >
          <Play className="h-3 w-3 fill-current" />
          {demoLabel}
        </Button>
        <button
          type="button"
          aria-label="Notifications"
          className="inline-flex items-center justify-center w-7 h-7 rounded-md text-muted-foreground hover:bg-surface-muted"
        >
          <Bell className="h-4 w-4" />
        </button>
        <button
          type="button"
          aria-label="Profile"
          className="inline-flex items-center justify-center w-7 h-7 rounded-md text-muted-foreground hover:bg-surface-muted"
        >
          <UserCircle2 className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
