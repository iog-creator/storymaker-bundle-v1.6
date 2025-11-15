# DRIFT_LOG.md - StoryMaker + AgentPM Drift Tracking

## Purpose

This document tracks drift from the Single Source of Truth (SSOT) and documents fixes applied to maintain system integrity.

## Drift Entries

### 2025-09-11 — SSOT v1.2 Closeout

- Drift fixed: unified model IDs, `/api/v1/*` only, envelope v1.2 everywhere.
- Guards added: model-lock, retrieval-smoke, proof-integrity, fresh-shell env.
- Policy: services fail-closed if providers not ready; "status:ok with empty payload" is prohibited.

### 2025-09-11 — Stability Fixes

- Issue: Services unstable; QA proofs empty; "status:ok" accepted without validation.
- Fix: Introduced new guards:
  - proof-integrity
  - rerank-monotonic
  - soak-and-concurrency
  - provider-isolation
  - fresh-shell-env
- SSOT v1.2 verified: proofs equal responses, services stable under load, providers isolated.

### 2025-09-11 — Legacy Route Blocking

- Issue: Legacy unversioned routes still accessible, causing API drift.
- Fix: Added `no_legacy_routes_guard.sh` to block non-v1 API usage.
- Result: All public endpoints now under `/api/v1/*` only.

### 2025-09-12 — Canonicalizer Drift Fix

- Issue: Proof hash drift due to canonicalization mismatch between service code (Python `json.dumps`) and guard scripts (jq).
- Root cause: `ci/json_hash.sh` used jq canonicalization instead of delegating to `ci/json_hash.py`.
- Fix applied:
  - Modified `ci/json_hash.sh` to delegate only to `ci/json_hash.py` (single source of truth)
  - Added `guards.canon.lint` target to prevent jq-based canonicalization
  - Hardened shell wrapper to fail-closed with no jq fallback
  - Added pre-commit hook for local dev protection
  - Updated CI to run canonicalizer verification before other guards
  - Added PR template with canonicalizer discipline checklist
- Result: Single canonicalizer enforced everywhere; zero drift vectors; comprehensive audit trails.

## Agents Pointerization + Proof Quality Gates (2025-09-12)

**PR-SSOT-REM-003 closeout.**

- Converted all workspace `AGENTS.md` copies to **pointer stubs** (no content forks)
- Added **QA Latency Guard** (latency_ms > 0, non-empty analysis, truthy `used`)
- Added **Rerank Monotonicity Guard** (scores must be non-increasing)
- Wired guards into Cursor rules + `Makefile` (`guards.qa.latency`, `guards.rerank.order`)
- Integrated into `ssot.guards` and CI; fail-closed on violations
 
 
