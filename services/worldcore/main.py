
# worldcore/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from services.common.envelope import envelope_ok, envelope_error
from services.guards.temporal import check_interval
from services.guards.allen_lite import validate_entity_consistency
import os
import re
import uuid
import time
from pathlib import Path

# Import routers lazily inside create_app to avoid side-effects at import time
def create_app() -> FastAPI:
    app = FastAPI(title="StoryMaker WorldCore", version="1.6.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    PROOFS_DIR = Path("docs/proofs/agentpm")

    # Lazy DAL initialization - only when needed
    _dal = None
    def get_dal():
        nonlocal _dal
        if _dal is None:
            DSN = os.environ.get("POSTGRES_DSN")
            if not DSN:
                raise RuntimeError("POSTGRES_DSN is required")
            from services.worldcore.dal import WorldCoreDAL
            _dal = WorldCoreDAL(DSN)
        return _dal

    @app.get("/health")
    def health():
        return {"status": "ok", "data": {"ok": True}}

    @app.get("/health/ready")
    def health_ready():
        """
        Active readiness: checks LM Studio (optional), Postgres (optional), proofs path.
        Never blocks > ~1.5s total.
        """
        meta = {"checks": {}, "latency_ms": 0}
        t0 = time.perf_counter()

        # proofs dir
        try:
            PROOFS_DIR.mkdir(parents=True, exist_ok=True)
            meta["checks"]["proofs_dir"] = {"ok": True, "path": str(PROOFS_DIR)}
        except Exception as e:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "error": f"proofs_dir: {e}",
                "meta": meta
            })

        # LM Studio (optional; only if OPENAI_API_BASE present)
        base = os.environ.get("OPENAI_API_BASE")
        if base:
            import http.client, urllib.parse, socket
            try:
                u = urllib.parse.urlparse(base)
                host = u.hostname or "127.0.0.1"
                port = u.port or (443 if u.scheme == "https" else 80)
                path = "/v1/models"
                conn = http.client.HTTPConnection(host, port, timeout=0.6) if u.scheme=="http" \
                       else http.client.HTTPSConnection(host, port, timeout=0.6)
                conn.request("GET", path, headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY','lm-studio')}"})
                resp = conn.getresponse()
                meta["checks"]["lm_studio"] = {"ok": (200 <= resp.status < 500), "status": resp.status}
            except (socket.timeout, Exception) as e:
                meta["checks"]["lm_studio"] = {"ok": False, "error": str(e)}

        # Postgres (optional; only if POSTGRES_DSN present)
        dsn = os.environ.get("POSTGRES_DSN")
        if dsn:
            try:
                import psycopg2
                conn = psycopg2.connect(dsn, connect_timeout=1)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    cur.fetchone()
                conn.close()
                meta["checks"]["postgres"] = {"ok": True}
            except Exception as e:
                meta["checks"]["postgres"] = {"ok": False, "error": str(e)}

        meta["latency_ms"] = int((time.perf_counter() - t0) * 1000)
        # Pass even if optional checks fail; signal via meta only.
        return {"status": "ok", "data": {"ready": True}, "meta": meta}

    @app.get("/diag/env")
    def diag_env():
        # Redact obvious secrets
        redacted = {}
        for k, v in os.environ.items():
            if any(s in k for s in ["KEY", "TOKEN", "PASSWORD", "SECRET"]):
                redacted[k] = "***"
            else:
                redacted[k] = v
        return {"status": "ok", "data": {"env": redacted}}

    @app.get("/diag/ping/lm")
    def diag_ping_lm():
        import time
        t0 = time.perf_counter()
        base = os.environ.get("OPENAI_API_BASE")
        if not base:
            return JSONResponse(status_code=400, content={
                "status": "error", "error": "OPENAI_API_BASE not set"
            })
        try:
            from openai import OpenAI
            client = OpenAI(base_url=base, api_key=os.environ.get("OPENAI_API_KEY","lm-studio"))
            # lightweight list; LM Studio handles this fast
            models = client.models.list()
            ms = int((time.perf_counter() - t0) * 1000)
            return {"status": "ok", "data": {"count": len(models.data)}, "meta": {"latency_ms": ms}}
        except Exception as e:
            return JSONResponse(status_code=502, content={
                "status": "error", "error": str(e)
            })

    # Valid entity types from OpenAPI spec
    VALID_ENTITY_TYPES = ["World", "Place", "Culture", "Faction", "Character", "Item", "Event"]
    VALID_STATUSES = ["DRAFT", "CANON"]

    class Entity(BaseModel):
        id: str = Field(..., min_length=1, max_length=100, description="Unique entity identifier")
        type: str = Field(..., description="Entity type")
        name: str = Field(..., min_length=1, max_length=200, description="Entity name")
        status: str = Field(..., description="Entity status")
        traits: Dict[str, Any] = Field(default_factory=dict, description="Entity traits")
        world_id: Optional[str] = Field(None, max_length=100, description="Parent world ID")
        summary: Optional[str] = Field(None, max_length=1000, description="Entity summary")
        
        @field_validator('type')
        @classmethod
        def validate_type(cls, v):
            if v not in VALID_ENTITY_TYPES:
                raise ValueError(f"Invalid entity type. Must be one of: {', '.join(VALID_ENTITY_TYPES)}")
            return v
        
        @field_validator('status')
        @classmethod
        def validate_status(cls, v):
            if v not in VALID_STATUSES:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
            return v
        
        @field_validator('id')
        @classmethod
        def validate_id_format(cls, v):
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
                raise ValueError("ID must start with letter and contain only letters, numbers, and underscores")
            return v

    class ApproveReq(BaseModel):
        cid: str = Field(..., min_length=1, description="Content ID to approve")

    @app.get("/health/legacy")
    def health_legacy():
        """Legacy health check endpoint - returns ok only when DB is reachable"""
        try:
            dal = get_dal()
            _ = dal.graph(None, None)
            return envelope_ok({"ok": True}, {"actor": "api"})
        except Exception as e:
            return envelope_error("DB_UNAVAILABLE", "Database not reachable", {"detail": str(e)}, {"actor": "api"})

    @app.post("/propose")
    def propose(entity: Entity):
        """Propose a new entity for approval"""
        try:
            # Validate entity consistency using Allen Lite guard
            consistency_issues = validate_entity_consistency(entity.model_dump())
            if consistency_issues:
                return envelope_error("VALIDATION_FAILED", "Entity consistency issues", 
                                    {"issues": consistency_issues}, {"actor": "api", "world_id": entity.world_id or ""})
            
            # Generate deterministic CID
            cid = f"b3:{abs(hash(entity.id)) % (10**8):08d}...{abs(hash(entity.name)) % (10**6):06d}"
            
            # Store proposal
            dal = get_dal()
            dal.propose(entity.model_dump(), cid)
            
            return envelope_ok({
                "cid": cid, 
                "id": entity.id, 
                "entity_type": entity.type,
                "status": "DRAFT"
            }, {"actor": "api", "world_id": entity.world_id or ""})
            
        except Exception as e:
            return envelope_error("PROPOSAL_FAILED", "Failed to create proposal", 
                                {"detail": str(e)}, {"actor": "api", "world_id": entity.world_id or ""})

    @app.post("/approve")
    def approve(req: ApproveReq):
        """Approve a proposal by CID (idempotent)"""
        try:
            dal = get_dal()
            pointer = dal.approve(req.cid)
            if not pointer.get("id"):
                return envelope_error("NOTHING_TO_APPROVE", "No proposals found or invalid CID", 
                                    {"cid": req.cid}, {"actor": "api", "cid": req.cid})
            
            return envelope_ok({"canon_pointer": pointer}, {"actor": "api", "cid": req.cid})
            
        except Exception as e:
            return envelope_error("APPROVAL_FAILED", "Failed to approve proposal", 
                                {"detail": str(e), "cid": req.cid}, {"actor": "api", "cid": req.cid})

    @app.get("/canon/entity/{id}")
    def get_canon(id: str):
        """Get canonical entity by ID"""
        try:
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', id):
                raise HTTPException(400, "Invalid entity ID format")
                
            dal = get_dal()
            c = dal.get_canon(id)
            if not c:
                raise HTTPException(404, "Entity not found")
                
            return envelope_ok({"entity": c["entity"]}, {"actor": "api"})
            
        except HTTPException:
            raise
        except Exception as e:
            return envelope_error("RETRIEVAL_FAILED", "Failed to retrieve entity", 
                                {"detail": str(e)}, {"actor": "api"})

    @app.get("/graph")
    def graph(world_id: Optional[str] = None, q: Optional[str] = None):
        """Get entity graph with optional filtering"""
        try:
            dal = get_dal()
            g = dal.graph(world_id, q)
            return envelope_ok(g, {"actor": "api", "world_id": world_id or ""})
            
        except Exception as e:
            # Fail-open with an empty graph so UI can render a stub without DB
            return envelope_ok({
                "nodes": [],
                "edges": [],
                "total_nodes": 0,
                "total_edges": 0
            }, {"actor": "api", "world_id": world_id or "", "warning": str(e)})

    @app.get("/proposals")
    def get_proposals(limit: int = 100):
        """Get pending proposals"""
        try:
            if limit > 1000:
                limit = 1000  # Cap to prevent abuse
                
            dal = get_dal()
            proposals = dal.get_proposals(limit)
            return envelope_ok({"proposals": proposals, "count": len(proposals)}, {"actor": "api"})
            
        except Exception as e:
            return envelope_error("PROPOSALS_FAILED", "Failed to retrieve proposals", 
                                {"detail": str(e)}, {"actor": "api"})

    # Routers (search, qa etc.)
    from services.worldcore.api import search, qa
    from services.worldcore.api_approve import router as approve_router
    app.include_router(search.router)  # Re-enabled - search API ready
    app.include_router(qa.router)  # QA endpoints for LM Studio checks
    app.include_router(approve_router)

    # Stable proofs count alias
    @app.get("/api/proofs/count")
    def proofs_count_alias():
        count = sum(1 for p in PROOFS_DIR.glob("*.json"))
        return {"status":"ok","data":{"count": count}}

    return app

# Uvicorn entrypoint expects a module-level "app"
app = create_app()
