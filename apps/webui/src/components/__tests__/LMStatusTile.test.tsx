import React from "react";
import { render, screen } from "@testing-library/react";
import { LMStatusTile } from "../LMStatusTile";
import type { LMIndicatorWidgetProps } from "../../utils/lmIndicatorAdapter";

const BASE_INDICATOR: LMIndicatorWidgetProps = {
  status: "healthy",
  reason: "ok",
  label: "LM Studio healthy",
  color: "green",
  icon: "status-healthy",
  tooltip_lines: ["Status: healthy"],
  metrics: {
    successRate: 0.95,
    errorRate: 0.05,
    totalCalls: 100,
    dbOff: false,
    topErrorReason: null,
    windowDays: 7,
    generatedAt: "2025-11-15T00:00:00Z",
  },
  source: { path: "/tmp" },
};

test("renders LM status label", () => {
  render(<LMStatusTile indicator={BASE_INDICATOR} />);
  expect(screen.getByText(/LM Status/i)).toBeInTheDocument();
  expect(screen.getByText(/LM Studio healthy/i)).toBeInTheDocument();
});
