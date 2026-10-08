import base64
import html
from pathlib import Path
from typing import Any

from foley.schemas import FoleyError
from foley.storage import Store, write_new


def audition(revisions: list[str], destination: Path, store: Path | str | None = None) -> dict[str, Any]:
    if not revisions or len(revisions) > 8:
        raise FoleyError("Select one to eight revisions for audition/compare.")
    library = Store(store)
    if destination.expanduser().resolve().is_relative_to(library.root):
        raise FoleyError("Save audition HTML outside the immutable revision library.")
    cards = []
    total = 0
    for revision in revisions:
        item = library.read(revision)
        data = (library.directory(revision) / "audio.wav").read_bytes()
        total += len(data)
        if total > 100_000_000:
            raise FoleyError("Audition exceeds 100 MB audio; choose fewer or shorter revisions.")
        audio = "data:audio/wav;base64," + base64.b64encode(data).decode()
        validation = item["validation"]
        loop_attribute = " loop" if item["scene"]["loop"] else ""
        playback = "Loop (repeats until paused)" if item["scene"]["loop"] else "One-shot"
        escape = html.escape
        cards.append(f"""<article><h2>{escape(item["title"])}</h2>
<p>{escape(item["original_brief"])}</p><p>{escape(item["change_request"] or "Original")}</p>
<p class="metadata">Revision {revision}<br>Parent: {item["parent"] or "none"} | Seed: {item["seed"]}<br>
{validation["duration"]:.3f}s | 48 kHz / 24-bit | {validation["channels"]} channel(s)
| peak {validation["peak_dbfs"]:.1f} dBFS<br>Playback: {playback}</p>
<audio controls{loop_attribute} preload="none" src="{audio}"></audio>
<p><a download="foley-{revision}.wav" href="{audio}">Download WAV</a></p>
<details><summary>Scene and provenance</summary><pre>{escape(str(item))}</pre></details></article>""")
    document = (
        """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; media-src data:; style-src 'unsafe-inline';">
<title>Foley audition</title><style>
:root{color-scheme:light dark;font-family:system-ui,sans-serif}body{max-width:1100px;margin:auto;padding:24px}
h1{font-size:2.4rem}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:24px}
article{border:1px solid #8886;border-radius:16px;padding:24px;min-width:0;background:#8881}
audio{width:100%}.metadata{font-size:.85rem;overflow-wrap:anywhere;opacity:.75}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.75rem}a{color:inherit;font-weight:600}
</style><h1>Foley audition</h1><p>Listen, compare and download. Procedural sound effects rendered with Csound.
No automatic playback, network dependencies or model calls. A boundary-smoothed loop is not a perceptual guarantee.</p><main>
"""
        + "\n".join(cards)
        + "</main></html>"
    )
    output = write_new(destination, document.encode("utf-8"))
    return {
        "path": str(output),
        "revisions": revisions,
        "bytes": output.stat().st_size,
        "self_contained": True,
        "listening_review": "pending human",
    }
