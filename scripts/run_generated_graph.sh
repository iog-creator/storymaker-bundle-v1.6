#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import asyncio, importlib.util
p="services/orchestration/generated/outline_graph.py"
spec=importlib.util.spec_from_file_location("outline_graph", p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
async def main():
    out = await m.run_graph({"premise": "A heist in a city of mirrors"})
    print(out)
asyncio.run(main())
PY


