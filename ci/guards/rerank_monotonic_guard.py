#!/usr/bin/env python3
import json, sys, pathlib, math

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROOFS = ROOT / "docs" / "proofs" / "agentpm"

def extract_scores(obj):
    # Accept several shapes: {"items":[{"score":..}]}, {"candidates":[{"score":..}]}, or {"results":[...]}
    for k in ("items","candidates","results"):
        arr = obj.get(k)
        if isinstance(arr, list) and arr and isinstance(arr[0], dict) and "score" in arr[0]:
            return [x.get("score") for x in arr]
    # Some tools put rerank under data
    d = obj.get("data", {})
    for k in ("items","candidates","results"):
        arr = d.get(k)
        if isinstance(arr, list) and arr and isinstance(arr[0], dict) and "score" in arr[0]:
            return [x.get("score") for x in arr]
    return None

bad = []
for p in PROOFS.rglob("*.json"):
    try:
        data = json.loads(p.read_text())
    except Exception:
        continue
    scores = extract_scores(data)
    if not scores or len(scores) < 2:
        continue
    # Require non-increasing order within a tiny epsilon
    eps = 1e-9
    for i in range(1, len(scores)):
        a, b = scores[i-1], scores[i]
        if a is None or b is None or not (isinstance(a,(int,float)) and isinstance(b,(int,float))):
            bad.append((str(p), f"non-numeric score at idx {i-1}->{i}: {a}->{b}"))
            break
        if b - a > eps:
            bad.append((str(p), f"non-monotonic at idx {i-1}->{i}: {a} < {b}"))
            break

if bad:
    for path, msg in bad:
        print(f"::error ::Rerank order violation in {path} — {msg}")
    sys.exit(1)
print("rerank_monotonic_guard: OK")
