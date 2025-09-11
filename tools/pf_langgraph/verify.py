from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from ruamel.yaml import YAML


def fingerprint_from_yaml(yaml_path: Path) -> str:
    yaml = YAML(typ="safe")
    spec = yaml.load(yaml_path.read_text())
    s = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaml", required=True)
    ap.add_argument("--py", required=True)
    args = ap.parse_args()

    expected = fingerprint_from_yaml(Path(args.yaml))
    spec = importlib.util.spec_from_file_location("_graph_mod", args.py)
    if spec is None or spec.loader is None:
        raise SystemExit("Failed loading generated module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    build_graph = getattr(mod, "build_graph", None)
    if not callable(build_graph):
        raise SystemExit("Missing build_graph() in generated module")
    g = build_graph()
    ok = getattr(g, "__spec_fingerprint__", None) == expected
    print(json.dumps({"ok": bool(ok)}))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()


