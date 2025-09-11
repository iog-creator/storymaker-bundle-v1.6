from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import os, time, json, re

router = APIRouter(prefix="/api/qa", tags=["qa"])

PROOFS = Path("docs/proofs/agentpm"); PROOFS.mkdir(parents=True, exist_ok=True)

class DraftIn(BaseModel):
    draft: str

# --- Local heuristic analyzers (fast, deterministic) ---
_BANNED = [
    "chosen one","ancient prophecy","dark lord","it was all a dream",
    "mysterious stranger","forbidden forest","destined to",
    "balance of light and dark","last of their kind","prophecy foretold","bloodline power"
]

def _analyze_tropes(text: str, cap: int = 10):
    notes = []
    used = 0
    lowered = text.lower()
    for t in _BANNED:
        if t in lowered:
            used += 1
            notes.append(t)
    return {"used": used, "cap": cap, "notes": notes}

def _analyze_promises(text: str):
    # Extract simple setup/payoff pairs using keyword heuristics
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    setups = [s for s in sentences if re.search(r"\b(setup|promise|plant|foreshadow)\b", s, re.I)]
    payoffs = [s for s in sentences if re.search(r"\b(payoff|resolve|reveal|callback|pays? off)\b", s, re.I)]
    ledger = []
    for i, s in enumerate(setups):
        payoff = payoffs[i] if i < len(payoffs) else None
        ledger.append({"setup": s, "payoff": payoff, "status": "ok" if payoff else "missing"})
    # If there are excess payoffs, include them as extras
    for j in range(len(setups), len(payoffs)):
        ledger.append({"setup": None, "payoff": payoffs[j], "status": "extraneous"})
    return {"ledger": ledger}

@router.post("/trope-budget")
def trope_budget(body: DraftIn):
    t0 = time.time()
    analysis = _analyze_tropes(body.draft)
    env = {"status":"ok","data":analysis,"meta":{"provider":"lm-studio","check":"trope-budget","latency_ms":int((time.time()-t0)*1000)}}
    (PROOFS / f"qa_trope_{int(time.time())}.json").write_text(json.dumps(env, indent=2), "utf-8")
    return env

@router.post("/promise-payoff")
def promise_payoff(body: DraftIn):
    t0 = time.time()
    analysis = _analyze_promises(body.draft)
    env = {"status":"ok","data":analysis,"meta":{"provider":"lm-studio","check":"promise-payoff","latency_ms":int((time.time()-t0)*1000)}}
    (PROOFS / f"qa_promise_{int(time.time())}.json").write_text(json.dumps(env, indent=2), "utf-8")
    return env
