import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** shadcn-style className combiner */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Pause for `ms` milliseconds (handy in async flows / play-demo). */
export const sleep = (ms: number) =>
  new Promise<void>((resolve) => setTimeout(resolve, ms));

/** Current time as "HH:MM UTC" (mirrors `nowUTC()` in standalone.html). */
export function nowUTC(): string {
  const iso = new Date().toISOString();
  return iso.slice(11, 16) + " UTC";
}

/** Pretty-print a relative timestamp from a millisecond epoch. */
export function formatTs(ts?: number): string {
  if (!ts) return "0.0s ago";
  const seconds = (Date.now() - ts) / 1000;
  if (seconds < 1) return "just now";
  return `${seconds.toFixed(1)}s ago`;
}

/** Downtime-saved INR figure (mirrors the impact-bar math). */
export function computeSaved(
  baselineMins: number,
  mttrMins: number,
  inrPerMin = 500,
): number {
  return Math.max(0, baselineMins - mttrMins) * inrPerMin;
}

/** Format INR with Indian-locale grouping. */
export function formatINR(amount: number): string {
  return amount.toLocaleString("en-IN");
}
