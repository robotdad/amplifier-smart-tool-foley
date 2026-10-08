"""Run with an installed wheel's Python, outside its checkout; no provider spend."""

import hashlib
import json
from pathlib import Path
import tempfile

from foley import lib


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="foley-installed-") as directory:
        root = Path(directory)
        store = root / "library"
        original = lib.render(lib.recipe("metal-impact", seed=17), store)
        variants = lib.variants(original["id"], [31, 32], store)
        audition = lib.audition([original["id"], variants[0]["id"]], root / "compare.html", store)
        exported = lib.export(original["id"], root / "effect.zip", True, store)
        repeated = lib.export(original["id"], root / "repeat.zip", True, store)
        assert exported["sha256"] == repeated["sha256"]
        assert len(lib.list_sounds(store)) == 3
        assert lib.inspect(original["id"], store)["validation"]["frames"] == 96000
        assert "data:audio/wav;base64," in Path(audition["path"]).read_text()
        for recipe in ("footsteps", "whoosh", "rain", "wind", "interface"):
            item = lib.render(lib.recipe(recipe, duration=1.5, channels=1), store)
            assert item["validation"]["channels"] == 1
            assert item["validation"]["subtype"] == "PCM_24"
        print(
            json.dumps(
                {
                    "status": "passed",
                    "installed_package": str(lib.skill_directory()),
                    "revisions": len(lib.list_sounds(store)),
                    "provider_calls": 0,
                    "export_sha256": exported["sha256"],
                    "audition_sha256": hashlib.sha256(Path(audition["path"]).read_bytes()).hexdigest(),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
