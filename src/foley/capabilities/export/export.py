import hashlib
import io
from pathlib import Path
from typing import Any
import zipfile

from foley.schemas import FoleyError
from foley.storage import PAYLOAD_FILES, Store, write_new


def export(revision: str, destination: Path, bundle: bool = False, store: Path | str | None = None) -> dict[str, Any]:
    library = Store(store)
    library.read(revision)
    root = library.directory(revision)
    if destination.expanduser().resolve().is_relative_to(library.root):
        raise FoleyError("Export outside the revision library to preserve immutable source files.")
    if bundle:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in (*PAYLOAD_FILES, "hashes.json"):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = 0o644 << 16
                archive.writestr(info, (root / name).read_bytes())
        data = buffer.getvalue()
    else:
        data = (root / "audio.wav").read_bytes()
    return {
        "id": revision,
        "path": str(write_new(destination, data)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "format": "zip" if bundle else "wav",
    }
