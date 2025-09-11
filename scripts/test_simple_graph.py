#!/usr/bin/env python3
import asyncio, json, os, importlib.util

def test_simple_graph():
    """Test just the first node to verify the graph structure works"""
    # Set environment variables
    os.environ["NARRATIVE_BASE"] = "http://127.0.0.1:8900"
    os.environ["WORLDCORE_BASE"] = "http://127.0.0.1:8900"
    
    # Load the generated graph module
    spec = importlib.util.spec_from_file_location("outline", "services/orchestration/generated/outline_graph.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    
    # Test just the first node function directly
    async def test_first_node():
        state = {"inputs": {"premise": "A hero must save the village"}, "nodes": {}, "outputs": {}}
        result = await m.node_narrative_outline(state, None, {})
        print("First node result:")
        print(json.dumps(result, indent=2))
        return result
    
    result = asyncio.run(test_first_node())
    return result

if __name__ == "__main__":
    test_simple_graph()


