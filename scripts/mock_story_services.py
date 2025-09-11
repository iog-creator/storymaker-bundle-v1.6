#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn, os, random, string
from datetime import datetime, timezone

# ---- Envelope helpers (inline to avoid imports) ----
def env_ok(data: Dict[str, Any] | None = None, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "status": "ok",
        "data": data or {},
        "error": None,
        "meta": {"ts": datetime.now(timezone.utc).isoformat(), **(meta or {})},
    }

def env_err(code: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "status": "error",
        "data": None,
        "error": {"code": code, "message": message, "details": details or {}},
        "meta": {"ts": datetime.now(timezone.utc).isoformat()},
    }

app = FastAPI(title="Mock Story Services")

# ---------- Narrative ----------
class OutlineIn(BaseModel):
    premise: str

@app.post("/narrative/outline")
def narrative_outline(inp: OutlineIn):
    rid = "D" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    outline = {
        "title": f"Outline from premise: {inp.premise}",
        "beats": ["Hook", "Inciting Incident", "Midpoint Twist", "Climax", "Resolution"],
        "proposal_id": rid,
    }
    return env_ok(outline)

# ---------- QA: trope budget ----------
class QADraft(BaseModel):
    draft: Any

@app.post("/api/qa/trope-budget")
def qa_trope_budget(inp: QADraft):
    # Toggle via env: TROPE_OK=true/false or by counting beats
    ok_env = os.environ.get("TROPE_OK", "").lower() in {"1","true","yes","y"}
    # Use TROPE_MAX to control the returned used value for testing
    trope_max = int(os.environ.get("TROPE_MAX", "10"))
    if trope_max < 10:  # If we want to force failure, return a high value
        used = 15  # Always return a value > 10 to force failure
    else:
        used = len(getattr(inp.draft, "get", lambda *_: [])("beats", [])) if isinstance(inp.draft, dict) else 7
    flags = {"ok": ok_env or used < 10}
    return env_ok({"used": used, "flags": flags})

# ---------- QA: promise/payoff ----------
@app.post("/api/qa/promise-payoff")
def qa_promise_payoff(inp: QADraft):
    ok_env = os.environ.get("PPOK", "").lower() in {"1","true","yes","y"}
    flags = {"ok": ok_env or True}
    return env_ok({"score": 0.91, "flags": flags})

# ---------- WorldCore approve ----------
class ApproveIn(BaseModel):
    action: str

@app.post("/api/events/{proposal_id}/approve")
def approve_event(proposal_id: str, inp: ApproveIn):
    if inp.action != "approve_canon":
        return env_err("bad_action", "Only approve_canon allowed", {"action": inp.action})
    return env_ok({"proposal_id": proposal_id, "approved": True})

if __name__ == "__main__":
    host = os.environ.get("MOCK_HOST", "127.0.0.1")
    port = int(os.environ.get("MOCK_PORT", "8900"))
    uvicorn.run(app, host=host, port=port)
