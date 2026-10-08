from pathlib import Path
import random
from typing import Any

from foley.scene import Scene
from foley.schemas import FoleyError
from foley.storage import Store


def variants(revision: str, seeds: list[int], store: Path | str | None = None) -> list[dict[str, Any]]:
    if not seeds or len(seeds) > 8 or len(set(seeds)) != len(seeds):
        raise FoleyError("Supply one to eight distinct seeds.")
    library = Store(store)
    original = library.read(revision)
    scenes = []
    for seed in seeds:
        data = dict(original["scene"])
        data["seed"] = seed
        rng = random.Random(seed)
        data["layers"] = [
            {
                **layer,
                "frequency": max(20, min(18000, layer["frequency"] * rng.uniform(0.96, 1.04))),
                "frequency_end": max(20, min(18000, layer["frequency_end"] * rng.uniform(0.96, 1.04))),
            }
            for layer in data["layers"]
        ]
        scenes.append(Scene.model_validate(data))
    # All inputs are validated before any rendering. Each published child is
    # independently usable; completed children survive a later rendering failure.
    return [
        library.publish(
            scene, original["original_brief"], f"Seeded variation {scene.seed}; pitch jitter up to 4%", revision
        )
        for scene in scenes
    ]
