#!/usr/bin/env python3
import asyncio, json, os, importlib.util

def test_sequential_fail():
    """Test the graph with failure path (trope budget exceeded)"""
    # Set environment variables
    os.environ["NARRATIVE_BASE"] = "http://127.0.0.1:8900"
    os.environ["WORLDCORE_BASE"] = "http://127.0.0.1:8900"
    os.environ["TROPE_MAX"] = "0"  # Force failure
    
    # Load the generated graph module
    spec = importlib.util.spec_from_file_location("outline", "services/orchestration/generated/outline_graph.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    
    async def run_sequential():
        print("🚀 Starting sequential graph execution (FAILURE PATH)...")
        state = {"inputs": {"premise": "A hero must save the village from a dragon"}, "nodes": {}, "outputs": {}}
        
        # Step 1: Generate outline
        print("📝 Step 1: Generating narrative outline...")
        state = await m.node_narrative_outline(state, None, {})
        print(f"✅ Outline generated: {state['nodes']['narrative_outline']['data']['title']}")
        
        # Step 2: QA trope budget
        print("🔍 Step 2: Analyzing trope budget...")
        state = await m.node_qa_trope_budget(state, None, {})
        trope_used = state['nodes']['qa_trope_budget']['data']['used']
        print(f"✅ Trope analysis: {trope_used} tropes used")
        
        # Step 3: QA promise payoff
        print("🎯 Step 3: Checking promise payoff...")
        state = await m.node_qa_promise_payoff(state, None, {})
        score = state['nodes']['qa_promise_payoff']['data']['score']
        print(f"✅ Promise payoff score: {score}")
        
        # Step 4: Decision gate
        print("🚪 Step 4: Evaluating decision gate...")
        state = await m.node_decide_gate(state, None, {})
        approved = state['nodes']['decide_gate']['data']['cond']
        print(f"✅ Decision: {'APPROVED' if approved else 'REJECTED'}")
        
        # Step 5: Approval (if applicable)
        if approved:
            print("✅ Step 5: Approving for canon...")
            state = await m.node_approve_canon(state, None, {})
            print(f"✅ Canon approval: {state['nodes']['approve_canon']['data']['approved']}")
        else:
            print("❌ Step 5: Skipped - story not approved (trope budget exceeded)")
        
        print("\n🎉 Sequential execution complete!")
        print("📊 Final state:")
        print(json.dumps(state, indent=2))
        return state
    
    result = asyncio.run(run_sequential())
    return result

if __name__ == "__main__":
    test_sequential_fail()

