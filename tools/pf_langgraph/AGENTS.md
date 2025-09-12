# Purpose
Promptflow to LangGraph conversion tools.

# Entrypoints & Commands
- Generate graph: `python -m tools.pf_langgraph.gen --in input.yaml --out output.py`
- Verify graph: `python -m tools.pf_langgraph.verify --yaml input.yaml --py output.py`

# Interfaces
- Command-line tools for graph generation
- YAML to Python conversion utilities

# Constraints
- Input must be valid Promptflow YAML
- Output must be valid LangGraph Python
- Handle conversion errors gracefully

# Gotchas
- YAML format must be specific
- Python output must be executable

# Pointers
- SSOT: `../../docs/SSOT/ssot.v1.2.yaml`
