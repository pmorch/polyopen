import json

from mashumaro.jsonschema import build_json_schema

from . import messages

schema_json = build_json_schema(messages.Message).to_json()

# But pretty print it
schema = json.loads(schema_json)
print(json.dumps(schema, sort_keys=True, indent=4))
