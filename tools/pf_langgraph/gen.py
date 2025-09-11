#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from ruamel.yaml import YAML

from .codegen import generate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="flow.dag.yaml")
    ap.add_argument("--out", dest="outp", required=True, help="generated .py")
    args = ap.parse_args()

    yaml = YAML(typ="safe")
    spec = yaml.load(Path(args.inp).read_text())
    code = generate(spec)
    outp = Path(args.outp)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(code)
    print(f"generated: {outp}")


if __name__ == "__main__":
    main()


