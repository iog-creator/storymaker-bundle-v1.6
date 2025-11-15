"""
Envelope validation library with jsonschema validation and invariants.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from jsonschema import validate as js_validate, ValidationError, Draft202012Validator

# Load the envelope schema
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "docs" / "schemas" / "envelope.schema.json"
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    ENVELOPE_SCHEMA = json.load(f)

# Create validator with additional properties disabled
VALIDATOR = Draft202012Validator(ENVELOPE_SCHEMA)


def _run_id() -> str:
    """Generate a unique run ID with timestamp and UUID suffix."""
    import uuid
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + f"-{str(uuid.uuid4())[:6].lower()}"


def _env_ok(data: Dict[str, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a valid OK envelope."""
    env = {
        "status": "ok",
        "data": data,
        "error": None,
        "meta": {
            "run_id": run_id or _run_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api",
            "schema_version": "1.1.0-pr000"
        },
    }
    return env


def _env_err(code: str, message: str, run_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a valid error envelope."""
    env = {
        "status": "error",
        "data": None,
        "error": {"code": code, "message": message},
        "meta": {
            "run_id": run_id or _run_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "api",
            "schema_version": "1.1.0-pr000"
        },
    }
    return env


def validate_envelope(data: Any) -> Tuple[bool, Optional[str], Optional[List[str]]]:
    """
    Validate data against envelope schema.
    
    Returns:
        (is_valid, error_code, violations)
    """
    try:
        # First check if it's a dict
        if not isinstance(data, dict):
            return False, "INVALID_TYPE", ["Data must be a JSON object"]
        
        # Check for additional properties (invariant: additionalProperties: false)
        violations = []
        for key in data.keys():
            if key not in ENVELOPE_SCHEMA["properties"]:
                violations.append(f"Additional property '{key}' not allowed")
        
        if violations:
            return False, "ADDITIONAL_PROPERTIES", violations
        
        # Check basic envelope structure
        if "status" not in data:
            return False, "MISSING_STATUS", ["Missing required field 'status'"]
        
        if "meta" not in data:
            return False, "MISSING_META", ["Missing required field 'meta'"]
        
        # Check status-specific invariants
        if data["status"] == "ok":
            if "data" not in data:
                return False, "MISSING_DATA", ["OK status requires 'data' field"]
            if data.get("error") is not None:
                return False, "INVALID_ERROR_FIELD", ["OK status must have error: null"]
        elif data["status"] == "error":
            if "error" not in data:
                return False, "MISSING_ERROR", ["Error status requires 'error' field"]
            if data.get("data") is not None:
                return False, "INVALID_DATA_FIELD", ["Error status must have data: null"]
        else:
            return False, "INVALID_STATUS", [f"Status must be 'ok' or 'error', got '{data['status']}'"]
        
        # Validate against JSON Schema
        js_validate(data, ENVELOPE_SCHEMA)
        return True, None, None
        
    except ValidationError as e:
        return False, "SCHEMA_VALIDATION_FAIL", [str(e)]
    except Exception as e:
        return False, "VALIDATION_ERROR", [str(e)]


def archive_invalid_payload(payload: Dict[str, Any], violations: List[str], proofs_dir: Path) -> str:
    """
    Archive an invalid payload to the proofs directory.
    
    Returns:
        run_id of the archived payload
    """
    run_id = _run_id()
    archive_dir = proofs_dir / run_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the invalid payload
    invalid_path = archive_dir / "invalid-envelope.json"
    with open(invalid_path, "w") as f:
        json.dump(payload, f, indent=2)
    
    # Create manifest with SHA and violation details
    with open(invalid_path, "rb") as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()
    
    manifest_lines = [
        f"sha256(invalid-envelope.json): {sha256_hash}",
        f"run_id: {run_id}",
        f"timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"violations: {len(violations)}",
        f"violation_details: {'; '.join(violations)}"
    ]
    
    with open(archive_dir / "manifest.txt", "w") as f:
        f.write("\n".join(manifest_lines))
    
    return run_id


def is_enveloped_response(data: Any) -> bool:
    """
    Check if data is already a valid envelope response.
    """
    is_valid, _, _ = validate_envelope(data)
    return is_valid
