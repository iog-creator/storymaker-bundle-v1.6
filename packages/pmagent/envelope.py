"""
Envelope system for pmagent - JSON v1.1 format validation and proof capture
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def generate_run_id() -> str:
    """Generate a run ID in the format YYYYMMDDTHHMMSSZ-abcdef"""
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    random_suffix = str(uuid.uuid4())[:6].lower()
    return f"{timestamp}-{random_suffix}"


def create_envelope(status: str, data: Optional[Dict[str, Any]] = None, 
                   error: Optional[Dict[str, str]] = None, 
                   run_id: Optional[str] = None) -> Dict[str, Any]:
    """Create an envelope in v1.1 format"""
    if run_id is None:
        run_id = generate_run_id()
    
    envelope = {
        "status": status,
        "data": data or {},
        "error": error,
        "meta": {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "cli",
            "schema_version": "1.1.0-pr000"
        }
    }
    
    return envelope


def hash_file(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    import hashlib
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
