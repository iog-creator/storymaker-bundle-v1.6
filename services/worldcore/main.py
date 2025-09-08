
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.common.envelope import envelope_ok, envelope_error
from services.worldcore.dal import WorldCoreDAL
import os

app = FastAPI(title="StoryMaker WorldCore", version="1.6.0")
DSN = os.environ.get("POSTGRES_DSN")
if not DSN: raise RuntimeError("POSTGRES_DSN is required")
dal = WorldCoreDAL(DSN)

class Entity(BaseModel):
    id: str; type: str; name: str; status: str; traits: dict
    world_id: Optional[str] = None; summary: Optional[str] = None

class ApproveReq(BaseModel):
    cid: str

@app.get("/health")
def health():
    try:
        _ = dal.graph(None, None)
        return envelope_ok({"ok": True})
    except Exception as e:
        return envelope_error("DB_UNAVAILABLE", "Database not reachable", {"detail": str(e)})

@app.post("/propose")
def propose(entity: Entity):
    cid = f"b3:{abs(hash(entity.id)) % (10**8):08d}...{abs(hash(entity.name)) % (10**6):06d}"
    dal.propose(entity.model_dump(), cid)
    return envelope_ok({"cid": cid, "id": entity.id, "entity_type": entity.type}, {"actor":"api","world_id": entity.world_id or ""})

@app.post("/approve")
def approve(req: ApproveReq):
    pointer = dal.approve(req.cid)
    if not pointer.get("id"):
        return envelope_error("NOTHING_TO_APPROVE","No proposals found or invalid CID", meta={"cid": req.cid})
    return envelope_ok({"canon_pointer": pointer}, {"cid": req.cid})

@app.get("/canon/entity/{id}")
def get_canon(id: str):
    c = dal.get_canon(id)
    if not c: raise HTTPException(404, "Not found")
    return envelope_ok({"entity": c["entity"]}, {"actor":"api"})

@app.get("/graph")
def graph(world_id: Optional[str] = None, q: Optional[str] = None):
    g = dal.graph(world_id, q)
    return envelope_ok(g, {"actor":"api", "world_id": world_id or ""})
