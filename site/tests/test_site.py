"""Exercise the real template build and fail-closed structural checker."""

import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def built(tmp_path: Path) -> Path:
    output = tmp_path / "pages"
    subprocess.run(
        [sys.executable, str(ROOT / "site/theme/build.py"), "--output", str(output)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return output


def run_check(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "site/check.py"), str(output)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_real_build_passes(built: Path) -> None:
    result = run_check(built)
    assert result.returncode == 0, result.stderr
    assert (built / "assets/theme-LICENSE.txt").read_bytes() == (ROOT / "site/theme/LICENSE").read_bytes()


def test_missing_asset_fails(built: Path) -> None:
    (built / "assets/mark-loop.png").unlink()
    assert run_check(built).returncode != 0


def test_bad_anchor_fails(built: Path) -> None:
    page = built / "index.html"
    page.write_text(page.read_text().replace('href="#get-started"', 'href="#not-here"'))
    assert "Missing anchor" in run_check(built).stderr


def test_fork_catalog_link_fails(built: Path) -> None:
    page = built / "index.html"
    page.write_text(
        page.read_text().replace(
            "https://microsoft.github.io/amplifier-smart-tools-catalog/",
            "https://robotdad.github.io/amplifier-smart-tools-catalog/",
        )
    )
    assert "Missing canonical destination" in run_check(built).stderr


def test_hidden_quality_limit_fails(built: Path) -> None:
    page = built / "index.html"
    page.write_text(page.read_text().replace("seamless ambience is not established", "seamless ambience"))
    assert "Missing disclosure" in run_check(built).stderr


def test_stray_output_fails(built: Path) -> None:
    (built / "private-log.txt").write_text("Not for publication")
    assert "Unexpected or missing published files" in run_check(built).stderr


def test_family_extension_preserves_canonical_owners() -> None:
    family = json.loads((ROOT / "site/theme/family.json").read_text())
    assert family["pages"]["foley"] == {
        "name": "Foley",
        "repository": "amplifier-smart-tool-foley",
        "owner": "robotdad",
    }
    for key in ("overview", "catalog"):
        assert family["pages"][key]["owner"] == "microsoft"


def test_theme_license_preserved() -> None:
    license_text = (ROOT / "site/theme/LICENSE").read_text()
    assert "Copyright (c) Microsoft Corporation" in license_text
    assert "Permission is hereby granted" in license_text


def test_actual_brand_media_and_background(built: Path) -> None:
    provenance = json.loads((ROOT / "site/assets/foley-brand-provenance.json").read_text())
    assert provenance["generator"]["revision"] == "bcdd7d25d29e42c0beb99e6e84426826"
    assert provenance["generator"]["amplifier_agent_engine"] == "0.20.0"
    for name, metadata in provenance["assets"].items():
        assert hashlib.sha256((built / "assets" / name).read_bytes()).hexdigest() == metadata["sha256"]
    page = (built / "index.html").read_text()
    assert 'style="background:#111820"' in page
    assert 'width="1186" height="284"' in page
    assert "Temporary template placeholder" not in page
    assert "Foley brand animation, created with Unfold" in page
    assert "<img data-brand-still hidden" in page
    assert "<video data-demo-video controls" in page
    assert ".product-image [hidden] { display: none; }" in (built / "assets/style.css").read_text()


def test_self_contained_preview_preserves_exact_media(built: Path, tmp_path: Path) -> None:
    output = tmp_path / "preview.html"
    subprocess.run(
        [sys.executable, str(ROOT / "site/preview.py"), str(built), str(output)],
        check=True,
    )
    text = output.read_text()
    assert "./assets/" not in text
    assert "<style>" in text
    assert "<script>document.addEventListener" in text
    encoded = re.search(r'data:video/mp4;base64,([^"]+)', text)
    assert encoded is not None
    assert base64.b64decode(encoded[1]) == (built / "assets/foley-logo-motion.mp4").read_bytes()


def test_unmodified_theme_files_match_provenance() -> None:
    provenance = json.loads((ROOT / "site/provenance.json").read_text())["theme"]
    for name, digest in provenance["upstream_sha256"].items():
        if name not in provenance["local_changes"]:
            assert hashlib.sha256((ROOT / "site/theme" / name).read_bytes()).hexdigest() == digest


def test_workflow_permissions_and_deploy_boundary() -> None:
    workflow = yaml.load((ROOT / ".github/workflows/website.yml").read_text(), Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"pull_request", "push", "workflow_dispatch"}
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert workflow["on"]["workflow_dispatch"]["inputs"]["publish"]["default"] == "false"
    assert workflow["permissions"] == {"contents": "read"}
    build = workflow["jobs"]["build"]
    assert "permissions" not in build
    assert build["steps"][0]["with"]["persist-credentials"] == "false"
    assert any(step.get("run") == "python site/check.py _site" for step in build["steps"])
    deploy = workflow["jobs"]["deploy"]
    assert deploy["needs"] == "build"
    assert deploy["permissions"] == {"pages": "write", "id-token": "write"}
    assert deploy["if"] == (
        "github.ref == 'refs/heads/main' && "
        "(github.event_name == 'push' ||\n"
        " (github.event_name == 'workflow_dispatch' && inputs.publish))"
    )
