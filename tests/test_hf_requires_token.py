import os, pytest
from services.narrative.scribe.hf_client import generate

@pytest.mark.skipif(bool(os.environ.get("GROQ_API_KEY","").strip()), reason="Token present; this test verifies fail-fast when missing")
def test_generate_requires_token_and_model():
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("GROQ_MODEL", None)
    with pytest.raises(RuntimeError):
        generate("logline", {"premise":"A harbor captain faces living fog."}, {"max_new_tokens":64})
