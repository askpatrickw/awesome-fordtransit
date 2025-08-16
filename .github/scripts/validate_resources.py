#!/usr/bin/env python3
import json, sys, pathlib
from jsonschema import Draft7Validator

SCHEMA_PATH = pathlib.Path('resources.schema.json')
DATA_PATH = pathlib.Path('resources.json')

def main():
    if not SCHEMA_PATH.exists() or not DATA_PATH.exists():
        print('Schema or data file missing', file=sys.stderr)
        return 2
    try:
        schema = json.loads(SCHEMA_PATH.read_text())
        data = json.loads(DATA_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f'JSON decode error: {e}', file=sys.stderr)
        return 2
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        print('Schema validation failed:')
        for e in errors:
            path = '/'.join(map(str, e.path)) or '<root>'
            print(f'- {path}: {e.message}')
        return 1
    print('resources.json schema validation OK')
    return 0

if __name__ == '__main__':
    sys.exit(main())
