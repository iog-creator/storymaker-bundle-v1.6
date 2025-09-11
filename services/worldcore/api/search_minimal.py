# worldcore/api/search_minimal.py - Minimal search router for testing
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os, time, json, math
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/search", tags=["search"])

# Minimal config
PROOFS_DIR = Path("docs/proofs/agentpm")
PROOFS_DIR.mkdir(parents=True, exist_ok=True)

class EmbedIn(BaseModel):
    text: str = Field(min_length=1, description="Text to embed")

class EmbedOut(BaseModel):
    embedding: List[float]
    dims: int
    model: str

class Candidate(BaseModel):
    id: Optional[str] = None
    text: str

class RerankIn(BaseModel):
    query: str = Field(min_length=1)
    candidates: List[Candidate] = Field(min_items=1)
    k: int = 5

class RerankItem(BaseModel):
    id: Optional[str] = None
    text: str
    score: float

class RerankOut(BaseModel):
    query: str
    top_k: List[RerankItem]

@router.post("/embed")
def post_embed(body: EmbedIn):
    """Placeholder embed endpoint - returns mock data"""
    # Mock embedding - 1024 dimensions of zeros
    mock_embedding = [0.0] * 1024
    data = EmbedOut(embedding=mock_embedding, dims=1024, model="mock").model_dump()
    meta = {"provider": "mock", "embedding_dims": 1024, "latency_ms": 1}
    return {"status": "ok", "data": data, "meta": meta}

@router.post("/rerank")
def post_rerank(body: RerankIn):
    """Placeholder rerank endpoint - returns mock data"""
    # Mock rerank - just return candidates in order with mock scores
    mock_items = []
    for i, c in enumerate(body.candidates[:body.k]):
        mock_items.append(RerankItem(id=c.id, text=c.text, score=1.0 - (i * 0.1)))
    
    data = RerankOut(query=body.query, top_k=mock_items).model_dump()
    meta = {"provider": "mock", "embedding_model": "mock", "embedding_dims": 1024, "latency_ms": 1}
    return {"status": "ok", "data": data, "meta": meta}
