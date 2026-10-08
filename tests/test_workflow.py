import base64
import hashlib
from html.parser import HTMLParser
import json
import os
import shutil
import zipfile

import pytest

from foley import lib
from foley.intelligence.schemas import AgentResult
from foley.scene import Scene
from foley.schemas import FoleyError


@pytest.fixture
def engine():
    if not shutil.which(os.environ.get("FOLEY_CSOUND", "csound")):
        pytest.skip("Csound is not installed; real rendering not verified")


class FakeIntelligence:
    implementation = "test-only"

    def preflight(self):
        pass

    def run(self, request):
        data = json.loads(request.prompt)
        assert request.output_schema is not None
        layer_schema = request.output_schema["$defs"]["Layer"]["properties"]
        expected = Scene.model_json_schema()["$defs"]["Layer"]["properties"]
        for field in ("duration", "attack", "release", "sustain"):
            assert layer_schema[field]["description"] == expected[field]["description"]
        scene = lib.recipe("metal-impact", data["duration"], data["seed"], data["channels"], data["loop"])
        return AgentResult(
            output=scene.model_dump(),
            provenance={"provider": request.provider, "model": request.model, "test_double": True},
        )


def snapshot(path):
    return {
        str(item.relative_to(path)): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in path.rglob("*")
        if item.is_file()
    }


def test_complete_create_revise_compare_export(engine, tmp_path):
    store = tmp_path / "library"
    intelligence = FakeIntelligence()
    first = lib.create("metal crash", store, duration=1, intelligence=intelligence)
    before = snapshot(store / first["id"])
    child = lib.revise(first["id"], "Longer ring", store, duration=3, intelligence=intelligence)
    assert child["parent"] == first["id"]
    assert child["original_brief"] == "metal crash"
    assert child["change_request"] == "Longer ring"
    assert child["validation"]["duration"] == 3
    assert snapshot(store / first["id"]) == before
    variants = lib.variants(child["id"], [22, 23], store)
    assert all(item["parent"] == child["id"] for item in variants)
    assert len(lib.list_sounds(store)) == 4
    assert lib.inspect(first["id"], store) == first
    html = tmp_path / "review.html"
    lib.audition([first["id"], child["id"]], html, store)
    assert html.read_text().count("<audio ") == 2
    assert "data:audio/wav;base64," in html.read_text()
    assert first["id"] in html.read_text()
    assert child["id"] in html.read_text()
    a = lib.export(child["id"], tmp_path / "a.zip", True, store)
    b = lib.export(child["id"], tmp_path / "b.zip", True, store)
    assert a["sha256"] == b["sha256"]
    with zipfile.ZipFile(a["path"]) as archive:
        assert set(archive.namelist()) == {"audio.wav", "scene.json", "scene.csd", "revision.json", "hashes.json"}
    wav = lib.export(first["id"], tmp_path / "a.wav", False, store)
    assert wav["sha256"] == first["validation"]["sha256"]
    with pytest.raises(FoleyError, match="already exists"):
        lib.export(first["id"], tmp_path / "a.wav", False, store)


def test_failure_leaves_original_and_no_partial_revision(engine, tmp_path, monkeypatch):
    original = lib.render(lib.recipe("wind"), tmp_path)
    before = snapshot(tmp_path)

    def fail(*args):
        raise FoleyError("Csound failed test")

    monkeypatch.setattr("foley.storage.render_audio", fail)
    with pytest.raises(FoleyError):
        lib.revise(original["id"], "change", tmp_path, intelligence=FakeIntelligence())
    assert {key: value for key, value in snapshot(tmp_path).items() if not key.startswith(".failures/")} == before
    assert len(list((tmp_path / ".failures").glob("*.json"))) == 1
    assert len(lib.list_sounds(tmp_path)) == 1
    assert not list(tmp_path.glob(".pending-*"))


@pytest.mark.parametrize("revision", ["../other", "/etc/passwd", ".", "..", "a" * 31, "A" * 32, "x" * 32])
def test_traversal_rejected(tmp_path, revision):
    with pytest.raises(FoleyError, match="Invalid revision"):
        lib.inspect(revision, tmp_path)


def test_tampering_and_symlink_rejected(engine, tmp_path):
    original = lib.render(lib.recipe("wind"), tmp_path / "library")
    directory = tmp_path / "library" / original["id"]
    audio = directory / "audio.wav"
    bytes_before = audio.read_bytes()
    audio.write_bytes(b"corrupt")
    with pytest.raises(FoleyError, match="integrity"):
        lib.export(original["id"], tmp_path / "out.wav", store=tmp_path / "library")
    audio.unlink()
    external = tmp_path / "original.wav"
    external.write_bytes(bytes_before)
    audio.symlink_to(external)
    with pytest.raises(FoleyError, match="redirected"):
        lib.inspect(original["id"], tmp_path / "library")


def test_markup_is_escaped(engine, tmp_path):
    data = lib.recipe("wind").model_dump()
    data["title"] = "<script>alert('bad')</script>"
    original = lib.render(Scene.model_validate(data), tmp_path / "library", brief="<img src=x onerror=alert(1)>")
    html = tmp_path / "review.html"
    lib.audition([original["id"]], html, tmp_path / "library")
    assert "<script>" not in html.read_text()
    assert "<img" not in html.read_text()
    assert "&lt;script&gt;" in html.read_text()


def test_bad_variants_have_no_partial_effect(engine, tmp_path):
    original = lib.render(lib.recipe("wind"), tmp_path)
    with pytest.raises(ValueError, match="seed"):
        lib.variants(original["id"], [99, -1], tmp_path)
    assert len(lib.list_sounds(tmp_path)) == 1


@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini", "chatgpt", "github"])
def test_explicit_selection_honored(engine, tmp_path, provider):
    item = lib.create("impact", tmp_path, provider=provider, model="caller-model", intelligence=FakeIntelligence())
    assert item["intelligence"]["model"] == "caller-model"
    assert item["intelligence"]["provider"] == {"chatgpt": "openai-chatgpt", "github": "github-copilot"}.get(
        provider, provider
    )


def test_provider_default_models(engine, tmp_path):
    from foley.schemas import DEFAULT_MODELS

    for provider, model in DEFAULT_MODELS.items():
        item = lib.create("impact", tmp_path, provider=provider, intelligence=FakeIntelligence())
        assert item["intelligence"]["model"] == model


def test_empty_submission_never_publishes(engine, tmp_path):
    class EmptyIntelligence(FakeIntelligence):
        def run(self, request):
            return AgentResult(error="NO_SUBMISSION")

    with pytest.raises(FoleyError, match="NO_SUBMISSION"):
        lib.create("impact", tmp_path, intelligence=EmptyIntelligence())
    assert lib.list_sounds(tmp_path) == []
    assert list((tmp_path / ".failures").glob("*.json"))


def test_changed_constraints_never_publish(engine, tmp_path):
    class WrongDuration(FakeIntelligence):
        def run(self, request):
            return AgentResult(output=lib.recipe("wind", duration=3).model_dump())

    with pytest.raises(FoleyError, match="changed required duration"):
        lib.create("impact", tmp_path, duration=2, intelligence=WrongDuration())
    assert lib.list_sounds(tmp_path) == []


def test_audition_honors_each_retained_loop_without_changing_audio(engine, tmp_path, monkeypatch):
    store = tmp_path / "library"
    items = [lib.render(lib.recipe("wind", duration=0.25, loop=loop), store) for loop in (False, True, False)]
    before = snapshot(store)

    def refuse_regeneration(*args):
        pytest.fail("Audition must reuse retained audio, not render it again")

    monkeypatch.setattr("foley.storage.render_audio", refuse_regeneration)
    destination = tmp_path / "audition.html"
    lib.audition([item["id"] for item in items], destination, store)

    class Players(HTMLParser):
        def __init__(self):
            super().__init__()
            self.audio: list[dict[str, str | None]] = []
            self.downloads: list[dict[str, str | None]] = []

        def handle_starttag(self, tag, attrs):
            if tag == "audio":
                self.audio.append(dict(attrs))
            if tag == "a":
                self.downloads.append(dict(attrs))

    players = Players()
    text = destination.read_text()
    players.feed(text)
    assert len(players.audio) == 3
    assert ["loop" in audio for audio in players.audio] == [False, True, False]
    assert all("autoplay" not in audio for audio in players.audio)
    assert all("controls" in audio for audio in players.audio)
    assert text.count("Playback: Loop (repeats until paused)") == 1
    assert text.count("Playback: One-shot") == 2
    for item, audio, download in zip(items, players.audio, players.downloads, strict=True):
        src = audio["src"]
        assert src is not None
        assert download["href"] == src
        assert download["download"] == f"foley-{item['id']}.wav"
        assert base64.b64decode(src.split(",", 1)[1]) == (store / item["id"] / "audio.wav").read_bytes()
    assert snapshot(store) == before
