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
    
    # Determine alwaysApply and globs based on rule type
    alwaysApply = False
    globs = []
    
    if name == "ssot_presence_gate":
        alwaysApply = True
    elif name == "provider_split_gate":
        alwaysApply = True
    elif name == "no_mocks_gate":
        globs = [".env", ".env.*", "Makefile", "scripts/**"]
    elif name == "env_config_guard":
        globs = [".env", ".env.*"]
    elif name == "proofs_location_gate":
        globs = ["docs/proofs/**", "**/proofs/**"]
    
    # Build guidance notes
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
    
    # Create the rule content as .mdc format
    rule_content = f"""---
description: {desc}
globs: {globs}
alwaysApply: {str(alwaysApply).lower()}
---
{desc}

{chr(10).join(guidance) if guidance else ''}"""
    
    return rule_content

def emit_mdc(rule_content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(rule_content)

def main():
    # Allow explicit list or default to all *.mdc
    inputs = sys.argv[1:] or [str(p) for p in SRC_DIR.glob("*.mdc")]
    for in_path in inputs:
        md = pathlib.Path(in_path).read_text(encoding="utf-8")
        meta, body = read_frontmatter(md)
        rule_content = cursor_rule(meta, body)
        rule_name = meta.get("name", "unnamed").replace("_", "-")
        out = DST_DIR / (rule_name + ".mdc")
        emit_mdc(rule_content, out)
        print(f"[rules] emitted {out}")

if __name__ == "__main__":
    main()
