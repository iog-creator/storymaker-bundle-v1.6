#!/usr/bin/env python3
import sys, re, pathlib, yaml, os

SRC_DIR = pathlib.Path("docs/SSOT/rules")
DST_DIR = pathlib.Path(".cursor/rules")
DST_DIR.mkdir(parents=True, exist_ok=True)

def read_frontmatter(md_text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md_text, flags=re.S)
    if not m:
        raise RuntimeError("Missing YAML front-matter")
    meta = yaml.safe_load(m.group(1)) or {}
    body = (m.group(2) or "").strip()
    return meta, body

def cursor_rule(meta, body):
    name = meta.get("name", "unnamed")
    desc = body.splitlines()[0].strip() if body else f"{name} (auto-applied rule)"
    # Defaults
    rule = {
        "name": name.replace("_","-"),
        "description": desc,
        # Cursor keys that control auto-attach behavior:
        # - alwaysApply: applies in all chats/edits
        # - globs: attaches when matching files are involved
        "alwaysApply": False,
        "globs": [],
        # Optional: 'run' could point at shell scripts if you want Cursor to suggest commands
        # For now we keep rules guidance-only (lightweight, no exec).
    }

    # Heuristics per your five rules
    if name == "ssot_presence_gate":
        rule["alwaysApply"] = True
    elif name == "provider_split_gate":
        rule["alwaysApply"] = True
    elif name == "no_mocks_gate":
        rule["globs"] = [".env", ".env.*", "Makefile", "scripts/**"]
    elif name == "env_config_guard":
        rule["globs"] = [".env", ".env.*"]
    elif name == "proofs_location_gate":
        rule["globs"] = ["docs/proofs/**", "**/proofs/**"]

    # Optional: attach a little "how to" guidance Cursor can show
    guidance = []
    if name == "provider_split_gate":
        guidance.append("Creative uses Groq (llama-3.3-70b-versatile). Embeddings/rerank use LM Studio at http://127.0.0.1:1234/v1.")
    if name == "no_mocks_gate":
        guidance.append("Production paths: DISABLE_MOCKS=1 and MOCK_LMS=0.")
    if name == "env_config_guard":
        guidance.append("Ensure OPENAI_API_BASE=http://127.0.0.1:1234/v1, OPENAI_API_KEY=lm-studio, EMBEDDING_DIMS=1024, GROQ_* present.")
    if name == "proofs_location_gate":
        guidance.append("Emit all envelopes under docs/proofs/agentpm/. Move strays there.")
    if name == "ssot_presence_gate":
        guidance.append("Defer to docs/SSOT/*. Avoid changes that drift from MASTER_PLAN, ASBUILT, MANUAL, VALIDATION_PROTOCOL.")

    if guidance:
        rule["notes"] = guidance

    return rule

def emit_yaml(rule, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(rule, f, sort_keys=False)

def main():
    # Allow explicit list or default to all *.mdc
    inputs = sys.argv[1:] or [str(p) for p in SRC_DIR.glob("*.mdc")]
    for in_path in inputs:
        md = pathlib.Path(in_path).read_text(encoding="utf-8")
        meta, body = read_frontmatter(md)
        rule = cursor_rule(meta, body)
        out = DST_DIR / (rule["name"] + ".yaml")
        emit_yaml(rule, out)
        print(f"[rules] emitted {out}")

if __name__ == "__main__":
    main()
