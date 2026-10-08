from pathlib import Path
from typing import Any

from foley.scene import Scene
from foley.storage import Store


def render(scene: Scene, store: Path | str | None = None, brief: str = "") -> dict[str, Any]:
    return Store(store).publish(scene, brief or scene.description or scene.title)
