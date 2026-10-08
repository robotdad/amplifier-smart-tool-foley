from pathlib import Path
from typing import Any

from foley.storage import Store


def list_sounds(store: Path | str | None = None) -> list[dict[str, Any]]:
    return Store(store).list()
