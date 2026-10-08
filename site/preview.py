"""Make a self-contained review copy without altering the deployed site."""

import argparse
import base64
import mimetypes
from pathlib import Path
import re


def preview(source: Path, destination: Path) -> None:
    """Inline exact built bytes; retain outbound links for ordinary browsers."""
    root = source.resolve()
    text = (root / "index.html").read_text()
    text = text.replace(
        '<link rel="stylesheet" href="./assets/style.css">',
        "<style>" + (root / "assets/style.css").read_text() + "</style>",
    )
    text = text.replace(
        '<script src="./assets/site.js" defer></script>',
        "<script>document.addEventListener('DOMContentLoaded', () => {\n"
        + (root / "assets/site.js").read_text()
        + "\n});</script>",
    )

    def inline(match: re.Match[str]) -> str:
        path = (root / match[1]).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Preview asset escaped the built site")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'"data:{mime};base64,{encoded}"'

    text = re.sub(r'"(\./assets/[^"]+)"', inline, text)
    if "./assets/" in text:
        raise ValueError("Unresolved external asset in self-contained preview")
    destination.parents[0].mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
    print(f"Self-contained preview: {destination} ({destination.stat().st_size} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    preview(args.source, args.destination)
