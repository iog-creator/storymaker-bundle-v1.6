import hashlib
import json
from typing import Dict, Any


def spec_fingerprint(spec: Dict[str, Any]) -> str:
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


