# Purpose
WorldCore: QA & Retrieval endpoints using **LM Studio** (Qwen).

# Entrypoints & Commands
- Run dev: `uvicorn services.worldcore.main:app --port 8000 --reload`
- QA trope: `POST /api/v1/qa/trope-budget`
- QA payoff: `POST /api/v1/qa/promise-payoff`
- Embed: `POST /api/v1/search/embed`
- Rerank: `POST /api/v1/search/rerank`

# Interfaces
- Provider: `lm-studio`
- Models:
  - Chat primary: `qwen/qwen3-8b`
  - Reasoning: `qwen/qwen3-4b-thinking-2507`
  - Reranker: `qwen.qwen3-reranker-0.6b`
  - Embedding: `text-embedding-qwen3-embedding-0.6b` (`dims=1024`)
- Envelope v1.2 + `proof.sha256`

# Constraints
- **Never** call Groq from here.
- QA must return **non-empty** analysis when `draft.length >= 30`; `latency_ms > 0`.
- Embeddings must be `1024` dims; rerank scores **descending**.

# Gotchas
- Warm up models on start (chat, embed, rerank) before `/health` goes green.
- Proof must equal response (guard compares sha256).

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
