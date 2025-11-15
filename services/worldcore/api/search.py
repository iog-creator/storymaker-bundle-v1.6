from fastapi import APIRouter
from pydantic import BaseModel, Field
from pathlib import Path
from openai import OpenAI
from typing import List, Optional
import os, time, json, math

router = APIRouter(prefix="/api/search", tags=["search"])
router_v1 = APIRouter(prefix="/api/v1/search", tags=["search-v1"])

OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:1234/v1")
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "lm-studio")
EMBED_MODEL     = os.environ.get("EMBEDDING_MODEL", "text-embedding-qwen3-embedding-0.6b")
EMBED_DIMS      = int(os.environ.get("EMBEDDING_DIMS", "1024"))
PROOFS          = Path("docs/proofs/agentpm"); PROOFS.mkdir(parents=True, exist_ok=True)

client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

class EmbedIn(BaseModel):
    text: str = Field(min_length=1)
class Candidate(BaseModel):
    id: Optional[str] = None
    text: str
class RerankIn(BaseModel):
    query: str = Field(min_length=1)
    candidates: List[Candidate]
    k: int = 5

def embed_text(txt: str):
    t0 = time.perf_counter()
    vec = client.embeddings.create(model=EMBED_MODEL, input=txt).data[0].embedding
    ms = int((time.perf_counter()-t0)*1000)
    return vec, ms
def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)) or 1e-12
    nb = math.sqrt(sum(y*y for y in b)) or 1e-12
    return dot/(na*nb)

# API v1 endpoints (primary)
@router_v1.post("/embed")
def post_embed_v1(body: EmbedIn):
    return _embed_handler(body)

@router_v1.post("/rerank")
def post_rerank_v1(body: RerankIn):
    return _rerank_handler(body)

# Legacy endpoints (deprecated)
@router.post("/embed")
def post_embed_legacy(body: EmbedIn):
    response = _embed_handler(body)
    if hasattr(response, 'headers'):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31"
        response.headers["Link"] = "</api/v1/search/embed>; rel=\"successor-version\""
    return response

@router.post("/rerank")
def post_rerank_legacy(body: RerankIn):
    response = _rerank_handler(body)
    if hasattr(response, 'headers'):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31"
        response.headers["Link"] = "</api/v1/search/rerank>; rel=\"successor-version\""
    return response

def _embed_handler(body: EmbedIn):
    vec, ms = embed_text(body.text)
    # Validate dims:1024 requirement
    assert len(vec) == 1024, f"Expected 1024 dims, got {len(vec)}"
    env = {"status":"ok","data":{"embedding":vec,"dims":len(vec),"model":EMBED_MODEL},
           "meta":{"provider":"lm-studio","embedding_dims":len(vec),"latency_ms":ms}}
    (PROOFS / f"embed_{int(time.time())}.json").write_text(json.dumps(env, indent=2), "utf-8")
    return env

def _rerank_handler(body: RerankIn):
    qv, qms = embed_text(body.query)
    scored = []
    tot = qms
    for c in body.candidates:
        ev, ms = embed_text(c.text)
        scored.append({"id":c.id, "text":c.text, "score":cosine(qv, ev)})
        tot += ms
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:max(1, body.k)]
    env = {"status":"ok","data":{"query":body.query,"top_k":top},
           "meta":{"provider":"lm-studio","embedding_model":EMBED_MODEL,"embedding_dims":EMBED_DIMS,"latency_ms":tot}}
    (PROOFS / f"rerank_{int(time.time())}.json").write_text(json.dumps(env, indent=2), "utf-8")
    return env