import os, pytest
from services.narrative.scribe.hf_client import generate

GROQ_TOKEN_PRESENT = bool(os.environ.get("GROQ_API_KEY", "").strip())

@pytest.mark.skipif(not GROQ_TOKEN_PRESENT, reason="GROQ_API_KEY not set; real Groq call required")
def test_hf_scene_generation_smoke():
    out = generate("scene", {
        "where": "Harbor of Lumen",
        "when": "night",
        "who": "Elyra; Captain Rios",
        "goal": "Inspect patrols before the storm",
        "obstacles": "Thick fog; missing skiff",
        "axis": "safety",
        "trope_bans": ["chosen one","ancient prophecy","dark lord"]
    }, {"temperature":0.8,"top_p":0.9,"max_new_tokens":400})
    assert out["provider"] == "groq"
    assert isinstance(out["draft"], str) and len(out["draft"]) > 0
    assert isinstance(out["issues"], list)
