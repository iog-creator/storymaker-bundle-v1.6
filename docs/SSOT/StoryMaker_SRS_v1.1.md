# SRS v1.1 — 2025-09-08
- Postgres 17 REQUIRED.
- Redis/MinIO required.
- Envelope/idempotency invariants.

## Acceptance (selected)
- A1: DB health gate (WorldCore `/health` ok only when DB reachable)
- A2: Approve idempotent
- A3: Temporal guard sane (Allen-lite)
- A4: Promise/Payoff ledger flags orphans
- A5: Trope budget enforced (per 1k words)
- A6: NPC WS proposes facts, never mutates canon
- A7: Screenplay export returns artifact envelope
- A8: Narrative creative generation uses **Groq 70B API exclusively**; service fails fast if `GROQ_API_KEY`/`GROQ_MODEL` not set. (No mocks or alternate providers.)
