from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import os, json, uuid

router = APIRouter()

APPROVABLE = {"characters","places","factions","cultures","items","events"}
PROOFS_DIR = os.environ.get("PROOFS_DIR", "docs/proofs/storymaker")

class ApproveIn(BaseModel):
    action: str = "approve_canon"

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def _envelope_ok(data: dict, meta: dict):
    return {"status":"ok","data":data,"error":None,"meta":meta}

@router.post("/api/{etype}/{eid}/approve")
def approve_entity(etype: str, eid: str, body: ApproveIn):
    if etype not in APPROVABLE:
        raise HTTPException(400, f"etype '{etype}' not approvable")
    if body.action != "approve_canon":
        raise HTTPException(400, "action must be 'approve_canon'")

    now = datetime.now(timezone.utc).isoformat()
    cid = str(uuid.uuid4())
    proof = {
        "ts": now,
        "cid": cid,
        "etype": etype,
        "id": eid,
        "op": "approve_canon",
        "result": {"canon": True},
    }

    _ensure_dir(PROOFS_DIR)
    path = os.path.join(PROOFS_DIR, f"approve_{etype}_{eid}_{cid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(proof, f, ensure_ascii=False, indent=2)

    meta = {
        "provider": "worldcore",
        "check": "approve_canon",
        "latency_ms": None,
        "proof_path": path,
        "cid": cid,
    }
    data = {"etype": etype, "id": eid, "canon": True}
    return _envelope_ok(data, meta)






