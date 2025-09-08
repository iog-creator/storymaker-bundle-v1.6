
# AGENTS.md — StoryMaker (v1.6 FINAL)
- DB required; fail fast if unavailable.
- Idempotent approve by CID.
- Envelope-only responses.
- Guards before merge (temporal, trope, promise/payoff).

Includes:
@./docs/AGENTS.style.md
@./docs/AGENTS.module.template.md
@./docs/Cursor_System_Prompt.md

## Narrative Creative Generation (Groq)
- Narrative calls **Groq API** with `GROQ_API_KEY` (Groq API key) and `GROQ_MODEL`.
- **70B model inference via Groq provider.**
- After generation, Narrative must run Trope Budget & Promise/Payoff and include issues in the Envelope.
### Runtime note
- `.env` is auto-loaded by the Makefile targets (`api.up`, `test`). You can also run:
  ```bash
  set -a; source .env; set +a
  ```

### Groq setup (Llama-3.3-70B)
- **Required**: Get Groq API key from https://console.groq.com/
- Set `GROQ_API_KEY=gsk_your_groq_api_key_here`
- Set `GROQ_MODEL=llama-3.3-70b-versatile`
- **Direct Groq API integration** - no HF router or endpoints needed.

## LM Studio Integration (Embeddings & Reranking)
- LM Studio handles **embeddings, reranking, and planning** (NOT creative generation)
- **Qwen 1024-dim embeddings** for content similarity and search
- **Chat-based reranking** for content quality scoring
- **Local model management** and health monitoring
- Set `LM_STUDIO_URL=http://127.0.0.1:1234`
- Set `LM_STUDIO_MODEL=qwen/qwen3-4b-2507`
