import json,glob,os
from jsonschema import validate
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
schema=json.load(open(os.path.join(ROOT,'docs/schemas/envelope.schema.json')))
for p in glob.glob(os.path.join(ROOT,'docs/openapi/examples/*.json')):
 data=json.load(open(p));
 # Only validate files that have both 'status' and 'meta' (envelope responses)
 if 'status' in data and 'meta' in data: 
     validate(instance=data, schema=schema)
