#!/usr/bin/env python3
"""
Back-compat shim. Older automation calls this script to emit Cursor rules.
This simply delegates to the canonical shell emitter.
"""
import os, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
emitter = ROOT / "tools" / "rules_emit.sh"
if not emitter.exists():
    print("rules emitter missing:", emitter, file=sys.stderr)
    sys.exit(1)
rc = subprocess.call(["bash", str(emitter)], cwd=str(ROOT))
sys.exit(rc)
