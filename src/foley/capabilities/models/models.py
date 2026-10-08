from typing import Any

from foley.intelligence.agent import discover
from foley.schemas import FoleyError


def models(provider: str) -> dict[str, Any]:
    result = discover(provider)
    if result.get("error"):
        raise FoleyError(result["error"])
    return result
