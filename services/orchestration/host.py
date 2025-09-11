from fastapi import FastAPI
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

@app.on_event("startup")
def _startup():
    global graph
    graph = build_graph_with_ctx(env=dict(os.environ)).compile()

@app.get("/healthz")
async def healthz():
    # Lightweight readiness for CI and Web UI
    from datetime import datetime, timezone
    return {"status": "ok", "meta": {"ts": datetime.now(timezone.utc).isoformat()}}

@app.post("/run")
async def run(inputs: dict):
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
