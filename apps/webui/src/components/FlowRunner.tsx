import { useState, useEffect } from "react";
import { runFlow, FlowRunResponse } from "../lib/api";
import MermaidPanel from "./MermaidPanel";

interface FlowState {
  status: "idle" | "running" | "completed" | "error";
  result?: FlowRunResponse;
  error?: string;
  premise?: string;
}

interface FlowRunnerProps {
  orchestrationBase?: string;
}

export default function FlowRunner({ 
  orchestrationBase = "http://127.0.0.1:8700" 
}: FlowRunnerProps) {
  const [state, setState] = useState<FlowState>({ status: "idle" });
  const [premise, setPremise] = useState("A heist story about a team of misfits");
  const [mermaidCode, setMermaidCode] = useState("");

  // Generate Mermaid diagram from flow state
  useEffect(() => {
    if (state.result?.state) {
      const { nodes, outputs } = state.result.state;
      const mermaid = generateMermaidDiagram(nodes, outputs);
      setMermaidCode(mermaid);
    }
  }, [state.result]);

  const handleRunFlow = async () => {
    if (!premise.trim()) return;
    
    setState({ status: "running", premise });
    
    try {
      const result = await runFlow({
        premise: premise.trim()
      });
      
      setState({ 
        status: "completed", 
        result, 
        premise 
      });
    } catch (error: any) {
      setState({ 
        status: "error", 
        error: error.message || "Unknown error occurred",
        premise 
      });
    }
  };

  const resetFlow = () => {
    setState({ status: "idle" });
    setMermaidCode("");
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="rounded-2xl border p-6 shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Story Flow Runner</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Story Premise
            </label>
            <textarea
              value={premise}
              onChange={(e) => setPremise(e.target.value)}
              placeholder="Enter your story premise..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={3}
              disabled={state.status === "running"}
            />
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={handleRunFlow}
              disabled={state.status === "running" || !premise.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {state.status === "running" ? "Running..." : "Run Flow"}
            </button>
            
            {state.status !== "idle" && (
              <button
                onClick={resetFlow}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Status Section */}
      {state.status !== "idle" && (
        <div className="rounded-2xl border p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Flow Status</h3>
          
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                state.status === "running" ? "bg-yellow-500 animate-pulse" :
                state.status === "completed" ? "bg-green-500" :
                state.status === "error" ? "bg-red-500" : "bg-gray-400"
              }`} />
              <span className="font-medium capitalize">{state.status}</span>
            </div>
            
            {state.premise && (
              <div>
                <span className="text-sm text-gray-600">Premise: </span>
                <span className="text-sm">{state.premise}</span>
              </div>
            )}
            
            {state.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <span className="text-sm text-red-600">{state.error}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Results Section */}
      {state.status === "completed" && state.result && (
        <div className="space-y-6">
          {/* Outline */}
          {state.result.data?.state?.nodes?.narrative_outline && (
            <div className="rounded-2xl border p-6 shadow-sm">
              <h3 className="text-lg font-semibold mb-4">Story Outline</h3>
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(state.result.data.state.nodes.narrative_outline, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* QA Results */}
          {(state.result.data?.state?.nodes?.qa_trope_budget || 
            state.result.data?.state?.nodes?.qa_promise_payoff) && (
            <div className="rounded-2xl border p-6 shadow-sm">
              <h3 className="text-lg font-semibold mb-4">Quality Assurance</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {state.result.data.state.nodes.qa_trope_budget && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Trope Budget</h4>
                    <pre className="text-xs text-blue-800 whitespace-pre-wrap">
                      {JSON.stringify(state.result.data.state.nodes.qa_trope_budget, null, 2)}
                    </pre>
                  </div>
                )}
                
                {state.result.data.state.nodes.qa_promise_payoff && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Promise Payoff</h4>
                    <pre className="text-xs text-green-800 whitespace-pre-wrap">
                      {JSON.stringify(state.result.data.state.nodes.qa_promise_payoff, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Approval Status */}
          {state.result.data?.state?.nodes?.decide_gate && (
            <div className="rounded-2xl border p-6 shadow-sm">
              <h3 className="text-lg font-semibold mb-4">Approval Status</h3>
              
              <div className={`p-4 rounded-lg ${
                state.result.data.state.nodes.decide_gate.data?.cond 
                  ? "bg-green-50 border border-green-200" 
                  : "bg-red-50 border border-red-200"
              }`}>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    state.result.data.state.nodes.decide_gate.data?.cond 
                      ? "bg-green-500" 
                      : "bg-red-500"
                  }`} />
                  <span className={`font-medium ${
                    state.result.data.state.nodes.decide_gate.data?.cond 
                      ? "text-green-900" 
                      : "text-red-900"
                  }`}>
                    {state.result.data.state.nodes.decide_gate.data?.cond 
                      ? "Approved" 
                      : "Rejected"}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Flow Diagram */}
          {mermaidCode && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Flow Diagram</h3>
              <MermaidPanel code={mermaidCode} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Generate Mermaid diagram from flow state
function generateMermaidDiagram(nodes: any, outputs: any): string {
  const nodeStates = Object.entries(nodes).map(([id, data]: [string, any]) => {
    const status = data?.status === "ok" ? "✅" : "❌";
    return `  ${id}["${status} ${id}"]`;
  }).join("\n");

  const edges = [
    "narrative_outline --> qa_trope_budget",
    "narrative_outline --> qa_promise_payoff", 
    "qa_trope_budget --> decide_gate",
    "qa_promise_payoff --> decide_gate",
    "decide_gate --> approve_canon"
  ].map(edge => `  ${edge}`).join("\n");

  return `graph TD
${nodeStates}
${edges}`;
}
