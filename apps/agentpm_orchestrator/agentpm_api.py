from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from jsonschema import validate as js_validate, ValidationError
from datetime import datetime, timezone
from pathlib import Path
import uuid
import json

REPO = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO / "docs" / "schemas" / "envelope.schema.json"
UI_DIR = REPO / "ui" / "agentpm_console"
PROOFS_DIR = REPO / "docs" / "proofs" / "agentpm"
APP_VERSION = "0.0.0-pr001"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    ENVELOPE_SCHEMA = json.load(f)

def _run_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + f"-{str(uuid.uuid4())[:6].lower()}"

def _env_ok(data: dict) -> dict:
    env = {
        "status": "ok",
        "data": data,
        "error": None,
        "meta": {
            "run_id": _run_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api",
            "schema_version": "1.1.0-pr000"
        },
    }
    js_validate(env, ENVELOPE_SCHEMA)
    return env

def _env_err(code: str, message: str) -> dict:
    env = {
        "status": "error",
        "data": None,
        "error": {"code": code, "message": message},
        "meta": {
            "run_id": _run_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api",
            "schema_version": "1.1.0-pr000"
        },
    }
    js_validate(env, ENVELOPE_SCHEMA)
    return env

app = FastAPI(title="AgentPM Orchestrator", version=APP_VERSION)

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
    except ValidationError as ve:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(ve))

@app.get("/agentpm/version")
def version():
    try:
        return _env_ok({"version": APP_VERSION, "schema": ENVELOPE_SCHEMA.get("$schema")})
    except ValidationError as ve:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(ve))

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
    except ValidationError as ve:
        return _env_err("ENVELOPE_VALIDATION_FAIL", str(ve))
