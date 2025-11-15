#!/usr/bin/env python3
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROOFS = ROOT / "docs" / "proofs" / "agentpm"

bad = []
for p in PROOFS.rglob("*.json"):
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        bad.append((str(p), f"invalid json: {e}"))
        continue
    # Heuristics: accept common fields; require latency_ms > 0 and non-empty analysis where present
    lat = data.get("latency_ms", None)
    if lat is None:
        # sometimes nested
        lat = data.get("meta", {}).get("latency_ms", None)
    if not (isinstance(lat, (int, float)) and lat > 0):
        bad.append((str(p), f"latency_ms invalid: {lat}"))
    analysis = data.get("analysis") or data.get("qa_analysis") or data.get("data", {}).get("analysis")
    if analysis is not None and (not isinstance(analysis, str) or not analysis.strip()):
        bad.append((str(p), "analysis empty"))
    used = data.get("used")
    if used is not None and used not in (True, 1, "1"):
        bad.append((str(p), f"used flag not truthy: {used}"))

if bad:
    for path, msg in bad:
        print(f"::error ::QA latency/analysis violation in {path} — {msg}")
    sys.exit(1)
print("qa_latency_guard: OK")
