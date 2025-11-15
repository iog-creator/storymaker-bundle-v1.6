# narrative/api.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import os, time, datetime, uuid
from services.narrative.services.generator import generate_outline
from services.narrative.providers.groq_client import get_config, GroqError
from services.common.proof_utils import write_proof

router = APIRouter(prefix="/narrative", tags=["narrative"])

class OutlineIn(BaseModel):
    world_id: str = Field(min_length=1)
    premise: str  = Field(min_length=1)
    mode: str     = Field(min_length=1)
    structure: Optional[str] = Field(default="harmon_8")
    max_beats: Optional[int] = Field(default=8)

@router.post("/outline")
def outline(body: OutlineIn, request: Request):
    t0 = time.perf_counter()
    
    # Get request ID from header or generate one
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    
    # Generate the outline
    res = generate_outline(body.world_id, body.premise, body.mode)
    ms = int((time.perf_counter() - t0) * 1000)

    if res.get("status") == "ok":
        # 1) Build data (may call Groq etc.)
        beats = res["data"].get("beats", [])
        issues = res["data"].get("issues", [])
        ledger = res["data"].get("ledger", {})
        analysis = res["data"].get("analysis", {})
        
        # 2) Assemble envelope (freeze meta once)
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        envelope = {
            "status": "ok",
            "data": {
                "beats": beats,
                "issues": issues,
                "ledger": ledger,
                "analysis": analysis
            },
            "error": None,
            "meta": {
                "ts": now,
                "actor": "ai",
                "world_id": body.world_id,
                "api_version": "v1.2",
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "role": "creative",
                "latency_ms": ms
            }
        }
        
        # 3) Write proof (hash over envelope without .proof)
        proofed = write_proof(envelope)
        
        # 4) Return response (exact same dict written)
        return proofed

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
