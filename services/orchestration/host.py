from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import MemorySaver
from tools.pf_langgraph.envelope import envelope_ok, envelope_err  # type: ignore
from datetime import datetime, timezone
import os

try:
    from services.orchestration.generated.outline_graph import (
        build_graph_with_ctx, _finalize_outputs
    )  # type: ignore
except Exception:  # pragma: no cover
    # Generated graph may not exist until first `make graph-generate`
    def build_graph_with_ctx(client=None, env=None):
        raise RuntimeError("Generated graph not found. Run 'make graph-generate' first.")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    global graph
    graph = build_graph_with_ctx(env=dict(os.environ)).compile()

@app.get("/health")
def health_root():
    return {"status": "ok", "service": "orchestration"}

@app.get("/api/v1/health")
async def health_v1():
    # Liveness probe - return 503 until dependencies ready
    from datetime import datetime, timezone
    try:
        # Check if graph is compiled and ready
        if 'graph' not in globals():
            return {"status": "error", "error": {"code": "not_ready", "message": "Graph not compiled"}}, 503
        return {"status": "ok", "service": "orchestration", "api": "v1", "meta": {"ts": datetime.now(timezone.utc).isoformat()}}
    except Exception as e:
        return {"status": "error", "error": {"code": "health_check_failed", "message": str(e)}}, 503

@app.get("/healthz")
async def healthz():
    # Lightweight readiness for CI and Web UI
    from datetime import datetime, timezone
    return {"status": "ok", "meta": {"ts": datetime.now(timezone.utc).isoformat()}}

@app.get("/version")
async def version():
    # Quick provenance check
    import subprocess
    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()[:8]
    except:
        git_sha = "unknown"
    
    spec_fingerprint = getattr(graph, '__spec_fingerprint__', 'unknown') if 'graph' in globals() else 'unknown'
    
    return {
        "status": "ok",
        "data": {
            "git_sha": git_sha,
            "spec_fingerprint": spec_fingerprint,
            "service": "orchestration-host"
        },
        "meta": {"ts": datetime.now(timezone.utc).isoformat()}
    }

@app.post("/api/v1/run")
async def run_v1(inputs: dict):
    """Primary API v1 endpoint for flow execution"""
    return await _run_flow(inputs)

@app.post("/run")
async def run_legacy(inputs: dict):
    """Legacy endpoint - deprecated, use /api/v1/run"""
    response = await _run_flow(inputs)
    if hasattr(response, 'headers'):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2025-12-31"
    return response

async def _run_flow(inputs: dict):
    try:
        state = {"inputs": inputs, "nodes": {}, "outputs": {}}
        state = await graph.ainvoke(state)  # type: ignore
        delta = _finalize_outputs(state)
        if isinstance(delta, dict) and 'outputs' in delta:
            try:
                state['outputs'] |= delta['outputs']
            except Exception:
                tmp = state.get('outputs', {}).copy()
                tmp.update(delta['outputs'])
                state['outputs'] = tmp
        
        # Write proof for AgentPM compliance
        import json
        from pathlib import Path
        proof_dir = Path("docs/proofs/agentpm")
        proof_dir.mkdir(parents=True, exist_ok=True)
        proof_file = proof_dir / f"orchestration_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        proof_data = {
            "status": "ok",
            "provider": "orchestration",
            "model": "langgraph",
            "data": {"state": state, "outputs": state.get("outputs", {})},
            "meta": {"ts": datetime.now(timezone.utc).isoformat(), "actor": "orchestration.host"}
        }
        with open(proof_file, 'w') as f:
            json.dump(proof_data, f, indent=2)
        
        return envelope_ok(
            data={"state": state, "outputs": state.get("outputs", {})},
            meta={"ts": datetime.now(timezone.utc).isoformat(), "actor": "orchestration.host"},
        )
    except Exception as e:  # pragma: no cover
        return envelope_err(
            code="graph_runtime_error",
            message=str(e),
            details={"inputs": inputs},
        )
