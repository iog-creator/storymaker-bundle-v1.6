import fs from "fs";
import path from "path";

import {
  loadLmIndicatorWidgetProps,
  LMIndicatorWidgetProps,
} from "../lmIndicatorAdapter";

const tmpPath = path.join(__dirname, ".tmp-indicator.json");

afterEach(() => {
  try {
    fs.unlinkSync(tmpPath);
  } catch {
    // ignore
  }
});

function writeIndicator(payload: unknown) {
  fs.writeFileSync(tmpPath, JSON.stringify(payload), "utf-8");
}

test("adapter returns healthy props", () => {
  writeIndicator({
    status: "healthy",
    reason: "ok",
    success_rate: 0.95,
    error_rate: 0.05,
    total_calls: 100,
    db_off: false,
    top_error_reason: null,
    window_days: 7,
    generated_at: "2025-11-15T00:00:00Z",
  });

  const props = loadLmIndicatorWidgetProps(tmpPath) as LMIndicatorWidgetProps;
  expect(props.status).toBe("healthy");
  expect(props.reason).toBe("ok");
  expect(props.color).toBe("green");
  expect(props.icon).toBe("status-healthy");
  expect(props.metrics.successRate).toBe(0.95);
  expect(props.metrics.errorRate).toBe(0.05);
});

test("adapter returns offline-safe on invalid JSON", () => {
  fs.writeFileSync(tmpPath, "{not json", "utf-8");
  const props = loadLmIndicatorWidgetProps(tmpPath) as LMIndicatorWidgetProps;
  expect(props.status).toBe("offline");
  expect(props.color).toBe("grey");
  expect(props.label).toMatch(/offline-safe/i);
});

test("adapter returns offline-safe on missing file", () => {
  const props = loadLmIndicatorWidgetProps(
    "/does/not/exist.json",
  ) as LMIndicatorWidgetProps;
  expect(props.status).toBe("offline");
  expect(props.metrics.dbOff).toBe(true);
});
