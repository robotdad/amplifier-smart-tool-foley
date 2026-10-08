"""Shared create/revise orchestration through the Intelligence contract."""

import json
from pathlib import Path
from typing import Any

from foley.audio import engine_path
from foley.intelligence.agent import canonical_provider
from foley.intelligence.interface import Intelligence, default_intelligence
from foley.intelligence.schemas import AgentRequest
from foley.scene import Scene
from foley.schemas import DEFAULT_MODELS, DEFAULT_PROVIDER, FoleyError, ReasoningEffort
from foley.storage import Store


def generate(
    brief: str,
    store: Path | str | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    duration: float = 2,
    channels: int = 2,
    seed: int = 1,
    loop: bool = False,
    reasoning_effort: ReasoningEffort = "medium",
    timeout: int = 300,
    parent: str | None = None,
    intelligence: Intelligence | None = None,
) -> dict[str, Any]:
    if not brief.strip() or len(brief) > 12000:
        raise FoleyError("Provide a nonempty brief/change request of at most 12000 characters.")
    provider = canonical_provider(provider)
    model = DEFAULT_MODELS[provider] if model is None else model
    if not model.strip():
        raise FoleyError("Specify a model ID supported by the selected provider; use foley models.")
    constraints = Scene.model_validate(
        {
            "duration": duration,
            "channels": channels,
            "seed": seed,
            "loop": loop,
            "crossfade_ms": min(20, duration * 250),
            "layers": [{"duration": duration, "attack": min(0.005, duration / 4), "release": min(0.1, duration / 4)}],
        }
    )
    library = Store(store)
    original = library.read(parent) if parent else None
    engine_path()
    request_data = {
        "request": brief,
        "duration": duration,
        "channels": channels,
        "seed": seed,
        "loop": loop,
        "previous_scene": original["scene"] if original else None,
    }
    output_schema = Scene.model_json_schema()
    for key in ("duration", "channels", "seed", "loop"):
        output_schema["properties"][key]["const"] = getattr(constraints, key)
    output_schema["required"] = ["layers", "duration", "channels", "seed", "loop"]
    request = AgentRequest(
        prompt=json.dumps(request_data),
        provider=provider,
        model=model,
        reasoning_effort=reasoning_effort,
        timeout_seconds=timeout,
        output_schema=output_schema,
    )
    result = (intelligence or default_intelligence()).run(request)
    if result.error or result.output is None:
        library.record_failure(
            "design",
            parent,
            {"provider": provider, "model": model, "published": False, "reason": "no_valid_submission"},
        )
        raise FoleyError(result.error or "NO_SUBMISSION: Agent did not submit a scene; no revision published.")
    try:
        scene = Scene.model_validate(result.output)
    except ValueError as exc:
        raise FoleyError(
            "Agent submitted an invalid scene. No revision published; simplify or clarify the request."
        ) from exc
    for key in ("duration", "channels", "seed", "loop"):
        if getattr(scene, key) != getattr(constraints, key):
            raise FoleyError(f"Agent changed required {key}; no revision published. Restate the requested constraints.")
    return library.publish(
        scene, original["original_brief"] if original else brief, brief if original else None, parent, result.provenance
    )
