import json
from pathlib import Path

from jsonschema import validate
from jsonschema.exceptions import ValidationError

SCHEMA_DIR = Path(__file__).parent / "schemas"


class SchemaValidationError(Exception):
    pass


def validate_schema(data: dict, event_name: str, version: int = 1):
    schema_full_path = SCHEMA_DIR / f"{event_name.lower().replace('.', '/')}/{version}.json"
    try:
        with open(schema_full_path, 'r') as schema_file:
            schema = json.load(schema_file)
    except FileNotFoundError as e:
        raise SchemaValidationError('Schema not found') from e

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise SchemaValidationError(f'Schema validation error: {e}') from e


__all__ = ["validate_schema", "SchemaValidationError"]
