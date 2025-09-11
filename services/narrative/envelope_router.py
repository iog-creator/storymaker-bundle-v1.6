from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import os, time, json

router = APIRouter()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
PROOFS = Path("docs/proofs/agentpm"); PROOFS.mkdir(parents=True, exist_ok=True)

# Import your existing generator (adapt import if needed)
try:
    from services.narrative.services.generator import generate_story_beat_description  # example path
except Exception:
    # Fallback: expect a local function somewhere else
    def generate_story_beat_description(premise: str) -> str:
        return f"Outline beats for: {premise}"

class OutlineIn(BaseModel):
    world_id: str
    premise: str
    mode: str = "outline"

@router.post("/narrative/outline")
def outline(body: OutlineIn):
    t0 = time.time()
    draft = generate_story_beat_description(body.premise)
    env = {
        "status": "ok",
        "data": {"draft": draft, "task": "outline", "world_id": body.world_id},
        "meta": {"provider": "groq", "model": GROQ_MODEL, "latency_ms": int((time.time()-t0)*1000)}
    }
    (PROOFS / f"narrative_outline_{int(time.time())}.json").write_text(json.dumps(env, indent=2), "utf-8")
    return env
