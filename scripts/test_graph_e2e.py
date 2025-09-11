#!/usr/bin/env python3
import asyncio, json, os, importlib.util

def test_graph_e2e(premise="A heist in a city of mirrors", trope_max=None):
    """Test the generated graph end-to-end"""
    # Set environment variables
    os.environ["NARRATIVE_BASE"] = "http://127.0.0.1:8900"
    os.environ["WORLDCORE_BASE"] = "http://127.0.0.1:8900"
    if trope_max is not None:
        os.environ["TROPE_MAX"] = str(trope_max)
    
    # Load the generated graph module
    spec = importlib.util.spec_from_file_location("outline", "services/orchestration/generated/outline_graph.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    
    async def run():
        out = await m.run_graph({"premise": premise})
        return out["outputs"]
    
    result = asyncio.run(run())
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        test_graph_e2e(trope_max=0)
    else:
        test_graph_e2e()


