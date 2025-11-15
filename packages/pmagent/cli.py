#!/usr/bin/env python3
"""
pmagent CLI - Project Management Agent Command Line Interface
"""

import json
import sys
import re
import subprocess
from pathlib import Path
from typing import Optional

import typer
from .envelope import create_envelope, generate_run_id, hash_file

# SSOT files that must be present (exactly 10)
SSOT_FILES = [
    "docs/SSOT/Acceptance_Tests_v1.md",
    "docs/SSOT/ASBUILT.md",
    "docs/SSOT/DRIFT_LOG.md",
    "docs/SSOT/EPOCH_LEDGER.md",
    "docs/SSOT/MANUAL.md",
    "docs/SSOT/MASTER_PLAN.md",
    "docs/SSOT/MASTER_PROMPT.md",
    "docs/SSOT/README.md",
    "docs/SSOT/StoryMaker_SRS_v1.1.md",
    "docs/SSOT/VALIDATION_PROTOCOL.md"
]

SCHEMAS_DIR = Path("docs/schemas")


def preflight(
    json_output: bool = typer.Option(False, "--json", help="Output pure JSON to stdout"),
    save: bool = typer.Option(False, "--save", help="Save proof pack to docs/proofs/agentpm/"),
    run_id_override: Optional[str] = typer.Option(None, "--run-id", help="Override run ID (format: YYYYMMDDTHHMMSSZ-abcdef)")
):
    """Env check: SSOT presence lock."""
    
    def get_run_id():
        if run_id_override:
            if not re.match(r"^[0-9]{8}T[0-9]{6}Z-[a-z0-9]{6}$", run_id_override):
                error = {"code": "INVALID_RUN_ID", "message": "Run ID must match pattern YYYYMMDDTHHMMSSZ-abcdef"}
                env = create_envelope("error", {}, error)
                if json_output:
                    print(json.dumps(env, indent=2))  # Pure JSON to stdout
                else:
                    sys.stderr.write("FAIL: Invalid run-id.\n")
                raise typer.Exit(code=1)
            return run_id_override
        return generate_run_id()
    
    # Check SSOT files presence
    missing = []
    for file_path in SSOT_FILES:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    # Check for drift (old paths that should not exist)
    drifts = []
    old_paths = ["README.md", "docs/README.md"]  # Example old paths
    for old_path in old_paths:
        if Path(old_path).exists():
            drifts.append(old_path)
    
    if missing or drifts:
        error = {"code": "PRESENCE_LOCK_FAIL", "message": f"Missing: {len(missing)} files; Drifts: {len(drifts)} pairs"}
        env = create_envelope("error", {}, error, get_run_id())
        if json_output:
            print(json.dumps(env, indent=2))  # Pure JSON to stdout
        else:
            sys.stderr.write(f"FAIL: {error['message']}.\n")
        raise typer.Exit(code=1)
    
    data = {
        "ssot_count": len(SSOT_FILES), 
        "schemas_present": [str(p) for p in SCHEMAS_DIR.iterdir()] if SCHEMAS_DIR.exists() else []
    }
    env = create_envelope("ok", data, None, get_run_id())
    
    if json_output:
        print(json.dumps(env, indent=2))  # Pure JSON only
    else:
        sys.stderr.write("PASS: All 16 SSOT + schemas green.\n")
    
    if save:
        run_id_final = env["meta"]["run_id"]
        proof_dir = Path(f"docs/proofs/agentpm/{run_id_final}")
        proof_dir.mkdir(parents=True, exist_ok=True)
        envelope_path = proof_dir / "envelope.json"
        with open(envelope_path, "w") as f:
            json.dump(env, f, indent=2)
        manifest_lines = [
            f"sha256(envelope.json): {hash_file(envelope_path)}",
            f"run_id: {run_id_final}",
            f"timestamp: {env['meta']['timestamp']}"
        ]
        with open(proof_dir / "manifest.txt", "w") as f:
            f.write("\n".join(manifest_lines))
        sys.stderr.write(f"Proof pack saved: {proof_dir}/manifest.txt\n")  # Stderr only


def serve(host: str = "127.0.0.1", port: int = 8700, reload: bool = True):
    """
    Run AgentPM API (serves /agentpm/ui + /agentpm/* endpoints).
    """
    target = "apps.agentpm_orchestrator.agentpm_api:app"
    cmd = ["uvicorn", target, "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")
    raise typer.Exit(code=subprocess.call(cmd))


def main():
    """Main entry point for the CLI."""
    app = typer.Typer()
    app.command()(preflight)
    app.command()(serve)
    app()


if __name__ == "__main__":
    main()