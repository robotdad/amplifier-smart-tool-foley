"""Provider-free structural checks for the generated Foley site."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE = Path(__file__).resolve().parents[0]


class Page(HTMLParser):
    """Collect links, assets and controls without a browser dependency."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.nodes: list[tuple[str, dict[str, str | None]]] = []
        self.ids: set[str] = set()
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.nodes.append((tag, values))
        if identity := values.get("id"):
            assert identity not in self.ids, f"Duplicate ID: {identity}"
            self.ids.add(identity)

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def check(output: Path) -> None:
    """Fail on missing assets, bad local navigation or misleading draft media."""
    output = output.resolve()
    page = Page()
    page.feed((output / "index.html").read_text())
    config = json.loads((SITE / "site.json").read_text())
    assert (output / ".nojekyll").is_file()
    assert sum(tag == "h1" for tag, _ in page.nodes) == 1
    hrefs = set()
    for tag, attrs in page.nodes:
        for key in ("href", "src", "poster", "data-motion-src", "data-still-src"):
            value = attrs.get(key)
            if not value:
                continue
            if key == "href":
                hrefs.add(value)
            url = urlsplit(value)
            if url.scheme or url.netloc:
                assert url.scheme == "https", f"Unsafe URL: {value}"
                assert url.netloc, f"Unsafe URL: {value}"
                assert not url.username, f"Credential URL: {value}"
                assert not url.password, f"Credential URL: {value}"
                continue
            assert not url.path.startswith("/"), f"Project Pages needs relative assets: {value}"
            if url.path:
                asset = (output / unquote(url.path)).resolve()
                assert asset.is_relative_to(output), f"Escaping asset: {value}"
                assert asset.is_file(), f"Missing asset: {value}"
                assert asset.stat().st_size, f"Empty asset: {value}"
            elif url.fragment:
                assert url.fragment in page.ids, f"Missing anchor: {value}"
        if tag == "img":
            assert "alt" in attrs
            assert attrs.get("width")
            assert attrs.get("height")
        if tag == "button" and attrs.get("data-copy"):
            assert attrs["data-copy"] in page.ids

    for required in (
        "https://microsoft.github.io/amplifier-smart-tools/",
        "https://microsoft.github.io/amplifier-smart-tools-catalog/",
        "https://microsoft.github.io/amplifier-smart-tools/spec/",
        "https://github.com/robotdad/amplifier-smart-tool-foley",
        "https://github.com/robotdad/amplifier-smart-tool-foley/blob/main/README.md",
    ):
        assert required in hrefs, f"Missing canonical destination: {required}"
    assert not any("robotdad.github.io/amplifier-smart-tools/" in href for href in hrefs)
    assert any("data-motion-toggle" in attrs for _, attrs in page.nodes)
    text = " ".join(page.text)
    for disclosure in (
        "not a hosted generator",
        "cannot listen",
        "did not measurably reduce",
        "seamless ambience is not established",
        "not live-tested",
        "not a Microsoft endorsement",
    ):
        assert disclosure in text, f"Missing disclosure: {disclosure}"
    assert config["install"] in text
    videos = [attrs for tag, attrs in page.nodes if tag == "video"]
    if config.get("video"):
        assert videos, "Configured video missing from generated page"
        for attrs in videos:
            assert all(key in attrs for key in ("controls", "muted", "loop", "playsinline", "poster"))
            assert "autoplay" not in attrs, "Reduced motion must be checked before starting"
        assert "View static logo" in text
        assert "Open animation" in text
    else:
        assert not videos, "Draft must not fabricate a logo video"
        assert "Temporary template placeholder" in (output / "index.html").read_text()
        assert "pending" in config["caption"]

    allowed = {
        "index.html",
        ".nojekyll",
        "assets/style.css",
        "assets/site.js",
        "assets/favicon.svg",
        "assets/theme-LICENSE.txt",
    }
    for folder in (SITE / "theme/assets", SITE / "assets"):
        if folder.is_dir():
            allowed.update(f"assets/{path.relative_to(folder)}" for path in folder.rglob("*") if path.is_file())
    actual = {str(path.relative_to(output)) for path in output.rglob("*") if path.is_file()}
    assert actual == allowed, f"Unexpected or missing published files: {actual ^ allowed}"
    assert not any(
        part.startswith(".") or part in {"__pycache__", "node_modules"}
        for path in actual - {".nojekyll"}
        for part in Path(path).parts
    ), "Private or generated input leaked into output"
    print(f"Site checks passed: {len(actual)} files, {len(hrefs)} link destinations.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    check(parser.parse_args().output)
