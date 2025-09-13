from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from jsonschema import validate as js_validate, ValidationError
from datetime import datetime, timezone
from pathlib import Path
import uuid
import json

from apps.agentpm_orchestrator.middleware import EnvelopeGateMiddleware
from packages.pmagent.pmagent.envelope_validator import (
    validate_envelope, archive_invalid_payload, _env_ok, _env_err
)

REPO = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO / "docs" / "schemas" / "envelope.schema.json"
UI_DIR = REPO / "ui" / "agentpm_console"
PROOFS_DIR = REPO / "docs" / "proofs" / "agentpm"
APP_VERSION = "0.0.0-pr002"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    ENVELOPE_SCHEMA = json.load(f)

app = FastAPI(title="AgentPM Orchestrator", version=APP_VERSION)

# Add envelope gate middleware
app.add_middleware(EnvelopeGateMiddleware)

@app.exception_handler(Exception)
async def _global_exc(req: Request, exc: Exception):
    return JSONResponse(content=_env_err("UNHANDLED_ERROR", str(exc)), status_code=500)

# Static mounts
if UI_DIR.exists():
    app.mount("/agentpm/ui", StaticFiles(directory=str(UI_DIR), html=True), name="agentpm_ui")
if SCHEMA_PATH.parent.exists():
    app.mount("/agentpm/schemas", StaticFiles(directory=str(SCHEMA_PATH.parent)), name="agentpm_schemas")

@app.get("/agentpm/healthz")
def healthz():
    try:
        return _env_ok({
            "schema_present": SCHEMA_PATH.exists(),
            "ui_present": UI_DIR.exists(),
            "proofs_dir": PROOFS_DIR.exists(),
            "version": APP_VERSION
        })
    except Exception as e:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(e))

@app.get("/agentpm/version")
def version():
    try:
        return _env_ok({"version": APP_VERSION, "schema": ENVELOPE_SCHEMA.get("$schema")})
    except Exception as e:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(e))

@app.get("/agentpm/proofs")
def proofs():
    try:
        if not PROOFS_DIR.exists():
            return _env_ok({"runs": []})
        runs = []
        for d in sorted(PROOFS_DIR.iterdir()):
            if not d.is_dir():
                continue
            runs.append({
                "run_id": d.name,
                "has_envelope": (d/"envelope.json").exists(),
                "has_manifest": (d/"manifest.txt").exists()
            })
        return _env_ok({"runs": runs})
    except Exception as e:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(e))

@app.post("/agentpm/validate")
async def validate(request: Request):
    """Validate arbitrary JSON payload against envelope schema."""
    try:
        payload = await request.json()
        
        # Validate the payload
        is_valid, error_code, violations = validate_envelope(payload)
        
        if is_valid:
            return _env_ok({
                "valid": True,
                "message": "Payload is a valid envelope"
            })
        else:
            # Archive invalid payload
            run_id = archive_invalid_payload(payload, violations or [], PROOFS_DIR)
            
            return _env_err(
                code=error_code or "VALIDATION_FAILED",
                message=f"Invalid envelope: {'; '.join(violations or [])}",
                run_id=run_id
            )
            
    except json.JSONDecodeError:
        return _env_err("INVALID_JSON", "Request body must be valid JSON")
    except Exception as e:
        return _env_err("VALIDATION_ERROR", str(e))
