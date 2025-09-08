
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from services.common.envelope import envelope_ok, envelope_error
from services.worldcore.dal import WorldCoreDAL
from services.guards.temporal import check_interval
from services.guards.allen_lite import validate_entity_consistency
import os
import re
import uuid

app = FastAPI(title="StoryMaker WorldCore", version="1.6.0")
DSN = os.environ.get("POSTGRES_DSN")
if not DSN: raise RuntimeError("POSTGRES_DSN is required")
dal = WorldCoreDAL(DSN)

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

@app.get("/health")
def health():
    """Health check endpoint - returns ok only when DB is reachable"""
    try:
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
        g = dal.graph(world_id, q)
        return envelope_ok(g, {"actor": "api", "world_id": world_id or ""})
        
    except Exception as e:
        return envelope_error("GRAPH_FAILED", "Failed to retrieve graph", 
                            {"detail": str(e)}, {"actor": "api", "world_id": world_id or ""})

@app.get("/proposals")
def get_proposals(limit: int = 100):
    """Get pending proposals"""
    try:
        if limit > 1000:
            limit = 1000  # Cap to prevent abuse
            
        proposals = dal.get_proposals(limit)
        return envelope_ok({"proposals": proposals, "count": len(proposals)}, {"actor": "api"})
        
    except Exception as e:
        return envelope_error("PROPOSALS_FAILED", "Failed to retrieve proposals", 
                            {"detail": str(e)}, {"actor": "api"})
