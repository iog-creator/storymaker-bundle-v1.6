# narrative/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os, time
from services.narrative.services.generator import generate_outline
from services.narrative.providers.groq_client import get_config, GroqError

router = APIRouter(prefix="/narrative", tags=["narrative"])

class OutlineIn(BaseModel):
    world_id: str = Field(min_length=1)
    premise: str  = Field(min_length=1)
    mode: str     = Field(min_length=1)

@router.post("/outline")
def outline(body: OutlineIn):
    t0 = time.perf_counter()
    res = generate_outline(body.world_id, body.premise, body.mode)
    ms = int((time.perf_counter() - t0) * 1000)

    if res.get("status") == "ok":
        return {"status": "ok", "data": res["data"], "meta": {"provider": "groq", "latency_ms": ms}}

    # fail-closed with a helpful 502
    raise HTTPException(
        status_code=502,
        detail={"status": "error", "error": res.get("error", "unknown"), "meta": {"latency_ms": ms, **res.get("meta", {})}},
    )

@router.get("/diag/provider")
def diag_provider():
    # Proves the provider wiring without doing a full generation
    try:
        cfg = get_config()
        return {"status": "ok", "data": {"provider": "groq", "model": cfg.model}}
    except GroqError as e:
        return {"status": "error", "error": "groq_misconfig", "meta": {"cause": str(e)}}
