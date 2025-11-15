/**
 * LM Indicator adapter for StoryMaker (Phase-5).
 *
 * - Hermetic: reads only Gemantria's lm_indicator.json file.
 * - Fail-closed: missing/invalid indicator -> offline-safe props.
 * - Contract: matches docs/SSOT/LM_WIDGETS.md in Gemantria.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

export type LmStatus = "offline" | "healthy" | "degraded";
export type LmReason = "db_off" | "no_calls" | "high_error_rate" | "ok";
export type LmColor = "grey" | "green" | "yellow" | "red";

export interface LMIndicatorWidgetMetrics {
  successRate: number | null;
  errorRate: number | null;
  totalCalls: number | null;
  dbOff: boolean;
  topErrorReason: string | null;
  windowDays: number;
  generatedAt: string;
}

export interface LMIndicatorWidgetProps {
  status: LmStatus;
  reason: LmReason;
  label: string;
  color: LmColor;
  icon: string;
  tooltip_lines: string[];
  metrics: LMIndicatorWidgetMetrics;
  source: { path: string };
}

// Path to Gemantria lm_indicator.json (adjust if your local layout differs)
// Use import.meta.url for ES modules compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const INDICATOR_PATH = path.resolve(
  __dirname,
  "../../../../Gemantria.v2/share/atlas/control_plane/lm_indicator.json",
);

const OFFLINE_SAFE_DEFAULT: LMIndicatorWidgetProps = {
  status: "offline",
  reason: "db_off",
  label: "LM status unknown (offline-safe mode)",
  color: "grey",
  icon: "status-offline",
  tooltip_lines: [
    "LM status unavailable",
    "Operating in offline-safe mode",
  ],
  metrics: {
    successRate: null,
    errorRate: null,
    totalCalls: null,
    dbOff: true,
    topErrorReason: null,
    windowDays: 7,
    generatedAt: "1970-01-01T00:00:00Z",
  },
  source: { path: INDICATOR_PATH },
};

interface RawIndicator {
  status?: string;
  reason?: string;
  success_rate?: number | null;
  error_rate?: number | null;
  total_calls?: number | null;
  db_off?: boolean;
  top_error_reason?: string | null;
  window_days?: number;
  generated_at?: string;
}

function toOptionalNumber(v: unknown): number | null {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isNaN(n) ? null : n;
}

function toOptionalString(v: unknown): string | null {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  return s.length === 0 ? null : s;
}

function toIntOr(v: unknown, fallback: number): number {
  const n = Number(v);
  return Number.isFinite(n) ? Math.trunc(n) : fallback;
}

function normalizeStatus(status: unknown): LmStatus {
  if (status === "healthy" || status === "degraded" || status === "offline") {
    return status;
  }
  return "offline";
}

function normalizeReason(reason: unknown): LmReason {
  if (
    reason === "db_off" ||
    reason === "no_calls" ||
    reason === "high_error_rate" ||
    reason === "ok"
  ) {
    return reason;
  }
  return "db_off";
}

function colorFor(ind: RawIndicator, status: LmStatus): LmColor {
  if (status === "offline") return "grey";
  if (status === "healthy") return "green";
  const err = toOptionalNumber(ind.error_rate);
  if (err !== null && err >= 0.5) return "red";
  return "yellow";
}

function iconFor(status: LmStatus): string {
  if (status === "offline") return "status-offline";
  if (status === "healthy") return "status-healthy";
  return "status-degraded";
}

function labelFor(status: LmStatus, reason: LmReason): string {
  if (status === "offline") {
    if (reason === "db_off") return "LM Studio offline (database unavailable)";
    if (reason === "no_calls")
      return "LM Studio offline (no recent activity)";
    return "LM Studio offline";
  }
  if (status === "degraded") {
    if (reason === "high_error_rate")
      return "LM Studio degraded (high error rate)";
    return "LM Studio degraded";
  }
  return "LM Studio healthy";
}

function tooltipLines(
  ind: RawIndicator,
  status: LmStatus,
  reason: LmReason,
): string[] {
  const sr = toOptionalNumber(ind.success_rate);
  const er = toOptionalNumber(ind.error_rate);
  const calls = toOptionalNumber(ind.total_calls);
  const windowDays = toIntOr(ind.window_days, 7);
  const topError = toOptionalString(ind.top_error_reason);
  const generatedAt = String(
    ind.generated_at ?? "1970-01-01T00:00:00Z",
  );

  const lines: string[] = [
    `Status: ${status}`,
    `Reason: ${reason}`,
    sr !== null ? `Success rate: ${(sr * 100).toFixed(1)}%` : "Success rate: n/a",
    er !== null ? `Error rate: ${(er * 100).toFixed(1)}%` : "Error rate: n/a",
    calls !== null
      ? `Total calls (last ${windowDays}d): ${calls}`
      : `Total calls (last ${windowDays}d): n/a`,
    topError ? `Top error: ${topError}` : "Top error: —",
    `As of: ${generatedAt}`,
  ];

  return lines;
}

export function loadLmIndicatorWidgetProps(
  customPath?: string,
): LMIndicatorWidgetProps {
  const p = customPath ?? INDICATOR_PATH;

  try {
    const rawText = fs.readFileSync(p, "utf-8");
    const data = JSON.parse(rawText) as RawIndicator;

    const status = normalizeStatus(data.status);
    const reason = normalizeReason(data.reason);

    const successRate = toOptionalNumber(data.success_rate);
    const errorRate = toOptionalNumber(data.error_rate);
    const totalCalls = toOptionalNumber(data.total_calls);
    const dbOff = Boolean(data.db_off ?? false);
    const topErrorReason = toOptionalString(data.top_error_reason);
    const windowDays = toIntOr(data.window_days, 7);
    const generatedAt = String(
      data.generated_at ?? "1970-01-01T00:00:00Z",
    );

    const color = colorFor(data, status);
    const icon = iconFor(status);
    const label = labelFor(status, reason);
    const tooltip = tooltipLines(data, status, reason);

    return {
      status,
      reason,
      label,
      color,
      icon,
      tooltip_lines: tooltip,
      metrics: {
        successRate,
        errorRate,
        totalCalls,
        dbOff,
        topErrorReason,
        windowDays,
        generatedAt,
      },
      source: { path: p },
    };
  } catch {
    return OFFLINE_SAFE_DEFAULT;
  }
}
