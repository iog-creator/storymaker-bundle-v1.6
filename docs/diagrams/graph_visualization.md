# Graph Visualization - StoryMaker v1.2

## Outline Graph (v1.2)

- **narrative_outline** → POST `/api/v1/narrative/outline` (Groq 70B)
- **qa_trope_budget** → POST `/api/v1/qa/trope-budget` (LM Studio, Qwen chat)
- **qa_promise_payoff** → POST `/api/v1/qa/promise-payoff` (LM Studio, Qwen chat)
- **embed** → POST `/api/v1/search/embed` (Qwen embedding, dims=1024)
- **rerank** → POST `/api/v1/search/rerank` (Qwen reranker)
- **decide_gate** → combines QA + retrieval; emits approval + evidence

All nodes emit envelope v1.2 and write proofs with `proof.sha256`.
