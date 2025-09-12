# StoryMaker System Status

## Services & Health (v1.2)

- **Endpoints**
  - WorldCore: `/api/v1/qa/*`, `/api/v1/search/*`, `/api/v1/graph`, `/api/v1/proofs/count`
  - Narrative: `/api/v1/narrative/outline`
  - Orchestration: `/api/v1/run`, `/api/v1/health`, `/api/v1/healthz`
- **Readiness**
  - Health is **red (503)** until:
    1) Groq reachable with `llama-3.3-70b-versatile`
    2) LM Studio models warmed: `qwen/qwen3-8b`, `qwen/qwen3-4b-thinking-2507`,
       `qwen.qwen3-reranker-0.6b`, `text-embedding-qwen3-embedding-0.6b`
    3) DB reachable
- **Provider Split**: Enforced at runtime and in CI.

## 🚀 QUICK START

```bash
# Start everything
./start-system.sh

# Or manually:
# 1. Mock services
TROPE_MAX=10 PYTHONPATH=. python3 scripts/mock_story_services.py &

# 2. Web UI  
cd apps/webui && npm run dev &

# 3. Open browser
# http://localhost:5173
```

## 📊 SYSTEM ARCHITECTURE

The Mermaid diagram shows:
- **User Interface Layer** → **Configuration** → **Code Generation** → **LangGraph Runtime**
- **Parallel QA execution** with safe state merging
- **Complete data flow** from YAML to execution
- **Visual representation** of all system components

## 🔧 KEY FILES

- `apps/webui/src/App.tsx` - Main React application
- `apps/webui/src/components/MermaidPanel.tsx` - Diagram renderer
- `scripts/mock_story_services.py` - Mock API server
- `tools/pf_langgraph/codegen.py` - LangGraph generator
- `services/orchestration/generated/outline_graph.py` - Generated graph
- `docs/diagrams/outline.mmd.md` - Mermaid diagram source

## ✅ VERIFIED WORKING

- [x] Web UI loads and renders
- [x] Mermaid diagram displays system architecture
- [x] Mock services respond to health checks
- [x] LangGraph generation works
- [x] Parallel execution with state merging
- [x] Visual system representation
- [x] Complete end-to-end workflow

**Status: LOCKED IN ✅**
