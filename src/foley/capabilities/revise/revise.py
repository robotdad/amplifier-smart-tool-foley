from pathlib import Path
from typing import Any

from foley.design import generate
from foley.intelligence.interface import Intelligence
from foley.schemas import DEFAULT_PROVIDER, ReasoningEffort
from foley.storage import Store


def revise(
    revision: str,
    changes: str,
    store: Path | str | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    duration: float | None = None,
    reasoning_effort: ReasoningEffort = "medium",
    timeout: int = 300,
    intelligence: Intelligence | None = None,
) -> dict[str, Any]:
    old = Store(store).scene(revision)
    return generate(
        changes,
        store,
        provider,
        model,
        duration if duration is not None else old.duration,
        old.channels,
        old.seed,
        old.loop,
        reasoning_effort,
        timeout,
        revision,
        intelligence,
    )
