#!/usr/bin/env python3
import json, sys
from pathlib import Path
from ruamel.yaml import YAML

def mermaid(spec):
    lines = ["flowchart TD"]
    nodes = {n["id"]: n for n in spec["nodes"]}
    for n in nodes.values():
        shape = "([{}])".format(n["id"]) if n["kind"]=="branch" else "([{}])".format(n["id"])
        lines.append(f'    {n["id"]}{shape}')
    for e in spec["edges"]:
        lines.append(f'    {e["from"]} --> {e["to"]}')
    # annotate simple branch outcomes
    for n in spec["nodes"]:
        if n["kind"]=="branch":
            on_t = (n["config"].get("on_true") or ["END"])[0]
            on_f = (n["config"].get("on_false") or ["END"])[0]
            if on_t!="END": lines.append(f'    {n["id"]} -- on_true --> {on_t}')
            if on_f!="END": lines.append(f'    {n["id"]} -- on_false --> {on_f}')
    return "\n".join(lines)

def main(inp, outp):
    spec = YAML(typ="safe").load(Path(inp).read_text())
    out = mermaid(spec)
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    Path(outp).write_text("```mermaid\n"+out+"\n```\n")
    print(json.dumps({"ok": True, "out": str(outp)}))

if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    main(in_path, out_path)
