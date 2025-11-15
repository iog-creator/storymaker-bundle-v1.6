import json
import jsonschema
from typing import Dict, Any

def validate_envelope_v1_2(envelope: Dict[str, Any]) -> bool:
    """Validate that envelope matches v1.2 schema"""
    schema_path = "docs/schemas/envelope.v1.2.schema.json"
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        jsonschema.validate(instance=envelope, schema=schema)
        return True
    except (jsonschema.ValidationError, FileNotFoundError) as e:
        print(f"Envelope validation failed: {e}")
        return False
