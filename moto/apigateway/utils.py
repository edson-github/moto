import string
import json
import yaml
from moto.moto_api._internal import mock_random as random
from typing import Any, Dict


def create_id() -> str:
    size = 10
    chars = list(range(10)) + list(string.ascii_lowercase)
    return "".join(str(random.choice(chars)) for _ in range(size))


def deserialize_body(body: str) -> Dict[str, Any]:
    try:
        api_doc = json.loads(body)
    except json.JSONDecodeError:
        api_doc = yaml.safe_load(body)

    return api_doc if "openapi" in api_doc or "swagger" in api_doc else {}


def to_path(prop: str) -> str:
    return f"/{prop}"
