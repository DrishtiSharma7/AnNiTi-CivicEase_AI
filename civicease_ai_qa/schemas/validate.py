"""Small JSON-schema checker (type, enum, required, properties, additionalProperties, items, minimum, maximum, $ref to
'definitions'). Enough to pin the response shapes the UI and agents rely on, with no extra dependency."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _is(v, t) -> bool:
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t]) and not (t != "boolean" and isinstance(v, bool) and t in ("object", "array", "string"))


def check(value, schema, root=None, path="$") -> list:
    root = root or schema
    errs = []
    if "$ref" in schema:
        return check(value, root["definitions"][schema["$ref"]], root, path)
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} not in {schema['enum']}"]
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is(value, t) for t in types):
            return [f"{path}: expected {types}, got {type(value).__name__}"]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errs += check(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unexpected field '{k}'")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += check(v, schema["items"], root, f"{path}[{i}]")
    return errs


def load(name: str) -> dict:
    return json.loads((HERE / f"{name}.schema.json").read_text())


def validate(value, name: str) -> list:
    return check(value, load(name))
