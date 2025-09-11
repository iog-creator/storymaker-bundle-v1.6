import asyncio, os, importlib.util, json
import httpx
import multiprocessing as mp
from time import sleep

def _serve():
    os.environ.setdefault("MOCK_HOST","127.0.0.1")
    os.environ.setdefault("MOCK_PORT","8900")
    os.environ.setdefault("PPOK","1")
    from scripts.mock_story_services import app
    import uvicorn
    uvicorn.run(app, host=os.environ["MOCK_HOST"], port=int(os.environ["MOCK_PORT"]))

def _start_mock():
    p = mp.Process(target=_serve, daemon=True); p.start()
    # Wait for port to open
    for _ in range(50):
        try:
            r = httpx.get("http://127.0.0.1:8900/docs", timeout=0.2)
            if r.status_code == 200:
                break
        except Exception:
            sleep(0.1)
    return p

def _load_generated():
    spec = importlib.util.spec_from_file_location("outline","services/orchestration/generated/outline_graph.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)  # type: ignore
    return m

def test_e2e_ok():
    p = _start_mock()
    try:
        os.environ["NARRATIVE_BASE"]="http://127.0.0.1:8900"
        os.environ["WORLDCORE_BASE"]="http://127.0.0.1:8900"
        m = _load_generated()
        async def run():
            st = await m.run_graph({"premise":"ok path"})
            return st
        st = asyncio.run(run())
        # Envelope-ish structure (state+outputs) and key nodes present
        assert isinstance(st, dict)
        assert "nodes" in st and "outputs" in st
        ns = st["nodes"]
        assert "narrative_outline" in ns and "qa_trope_budget" in ns and "qa_promise_payoff" in ns
        # Branch cond recorded
        assert "decide_gate" in ns and "data" in ns["decide_gate"]
        assert ns["decide_gate"]["data"]["cond"] is True
        assert st["outputs"]["approved"] is True
        assert isinstance(st["outputs"]["qa"]["trope"]["used"], int)
    finally:
        p.terminate()

def test_e2e_blocked():
    p = _start_mock()
    try:
        os.environ["NARRATIVE_BASE"]="http://127.0.0.1:8900"
        os.environ["WORLDCORE_BASE"]="http://127.0.0.1:8900"
        os.environ["TROPE_MAX"]="0"  # force gate false
        m = _load_generated()
        async def run():
            st = await m.run_graph({"premise":"blocked path"})
            return st
        st = asyncio.run(run())
        ns = st["nodes"]
        assert "qa_trope_budget" in ns and "qa_promise_payoff" in ns
        assert "decide_gate" in ns and ns["decide_gate"]["data"]["cond"] is False
        assert "outputs" in st and st["outputs"].get("approved") is False
    finally:
        p.terminate()


