"""Immutable revisions published only after the renderer validates delivery."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any
import uuid

from foley.audio import render_audio
from foley.scene import Scene
from foley.schemas import FoleyError

ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")
PAYLOAD_FILES = ("audio.wav", "scene.json", "scene.csd", "revision.json")


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"


class Store:
    def __init__(self, root: Path | str | None = None) -> None:
        self.root = Path(root or os.environ.get("FOLEY_HOME", "~/.local/share/foley")).expanduser().resolve()

    def directory(self, revision: str) -> Path:
        if not ID_PATTERN.fullmatch(revision):
            raise FoleyError("Invalid revision ID; use the 32-character ID returned by create, render or list.")
        path = self.root / revision
        if path.is_symlink() or not path.is_dir():
            raise FoleyError("Revision not found in this library; check --store and foley list.")
        return path

    def read(self, revision: str) -> dict[str, Any]:
        root = self.directory(revision)
        try:
            for name in (*PAYLOAD_FILES, "hashes.json"):
                if (root / name).is_symlink() or not (root / name).is_file():
                    raise FoleyError("Revision has missing or redirected files; restore it from an intact export.")
            hashes = json.loads((root / "hashes.json").read_text())
            for name in PAYLOAD_FILES:
                if hashlib.sha256((root / name).read_bytes()).hexdigest() != hashes[name]:
                    raise FoleyError("Revision integrity check failed; restore it from an intact export.")
            result = json.loads((root / "revision.json").read_text())
            if result["id"] != revision:
                raise FoleyError("Revision identity mismatch; restore the intact library.")
            Scene.model_validate_json((root / "scene.json").read_text())
            return result
        except (ValueError, KeyError, OSError) as exc:
            raise FoleyError("Revision metadata is malformed; restore it from an intact export.") from exc

    def scene(self, revision: str) -> Scene:
        self.read(revision)
        return Scene.model_validate_json((self.directory(revision) / "scene.json").read_text())

    def record_failure(self, phase: str, parent: str | None, details: dict[str, Any]) -> None:
        """Best-effort diagnostic receipt, never a replacement for the real failure."""
        try:
            directory = self.root / ".failures"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"{uuid.uuid4().hex}.json").write_text(
                json_text({"phase": phase, "parent": parent, **details})
            )
        except OSError:
            pass

    def publish(
        self,
        scene: Scene,
        brief: str,
        change_request: str | None = None,
        parent: str | None = None,
        intelligence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scene = Scene.model_validate(scene.model_dump())
        if parent:
            self.read(parent)
        self.root.mkdir(parents=True, exist_ok=True)
        revision = uuid.uuid4().hex
        pending = Path(tempfile.mkdtemp(prefix=".pending-", dir=self.root))
        try:
            csd, validation = render_audio(scene, pending / "audio.wav")
            result = {
                "id": revision,
                "parent": parent,
                "title": scene.title,
                "original_brief": brief,
                "change_request": change_request,
                "seed": scene.seed,
                "validation": validation,
                "intelligence": intelligence,
                "scene": scene.model_dump(),
            }
            (pending / "scene.csd").write_text(csd)
            (pending / "scene.json").write_text(json_text(scene.model_dump()))
            (pending / "revision.json").write_text(json_text(result))
            hashes = {name: hashlib.sha256((pending / name).read_bytes()).hexdigest() for name in PAYLOAD_FILES}
            (pending / "hashes.json").write_text(json_text(hashes))
            pending.rename(self.root / revision)
            return result
        except Exception:
            self.record_failure("render", parent, {"seed": scene.seed, "scene": scene.model_dump(), "published": False})
            raise
        finally:
            if pending.exists():
                shutil.rmtree(pending)

    def list(self) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        return [self.read(path.name) for path in sorted(self.root.iterdir()) if ID_PATTERN.fullmatch(path.name)]


def write_new(destination: Path, data: bytes) -> Path:
    """Never silently replace an existing user artifact."""
    destination = destination.expanduser().absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as handle:
            handle.write(data)
    except FileExistsError as exc:
        raise FoleyError("Destination already exists; choose a new export/audition filename.") from exc
    return destination
