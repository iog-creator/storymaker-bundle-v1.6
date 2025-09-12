import hashlib, json, os, datetime, uuid
from typing import Any, Dict

PROOFS_ROOT = os.getenv("PROOFS_ROOT", "docs/proofs/agentpm")

def _canonical_bytes_without_proof(envelope: dict) -> bytes:
    # EXACT contract used by guards (ci/json_hash.py)
    clean = dict(envelope)
    clean.pop("proof", None)
    s = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")

def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":"))

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def write_proof(envelope: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.datetime.utcnow()
    day_path = os.path.join(PROOFS_ROOT, now.strftime("%Y/%m/%d"))
    os.makedirs(day_path, exist_ok=True)
    pid = envelope.get("proof",{}).get("id") or str(uuid.uuid4())
    envelope.setdefault("proof", {})["id"] = pid
    path = os.path.join(day_path, f"{pid}.json")

    # compute sha over canonicalized API response WITHOUT .proof field (contract canon-v1)
    digest = hashlib.sha256(_canonical_bytes_without_proof(envelope)).hexdigest()
    
    # add proof fields to envelope
    envelope["proof"]["sha256"] = digest
    envelope["proof"]["path"] = path
    envelope["proof"]["written"] = True
    envelope["proof"]["format"] = "canon-v1"

    # write modified envelope to file
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(envelope, indent=2))
    return envelope
