from pathlib import Path
from typing import Any

from foley.storage import Store


def inspect(revision: str, store: Path | str | None = None) -> dict[str, Any]:
    return Store(store).read(revision)
