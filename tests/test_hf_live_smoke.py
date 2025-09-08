import os, pytest
from services.narrative.scribe.hf_client import generate

GROQ_TOKEN_PRESENT = bool(os.environ.get("GROQ_API_KEY", "").strip())

@pytest.mark.skipif(not GROQ_TOKEN_PRESENT, reason="GROQ_API_KEY not set; live Groq smoke test skipped")
def test_hf_live_scene_small_gen():
    # Keep tokens modest to minimize spend; still verifies end-to-end call and longform defaults.
    out = generate("scene", {
        "where":"Harbor of Lumen",
        "when":"night",
        "who":"Elyra; Captain Rios",
        "goal":"Inspect the patrols before the storm",
        "obstacles":"Fog; a missing skiff",
        "axis":"safety",
        "trope_bans":["chosen one","ancient prophecy","dark lord"]
    }, {"max_new_tokens": 256})
    assert out["provider"] == "groq"
    assert isinstance(out["draft"], str) and len(out["draft"]) > 0
    assert "issues" in out
