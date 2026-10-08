import hashlib
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest
import soundfile as sf

from foley import lib
from foley.audio import compile_scene, read_audio, render_audio
from foley.scene import Layer, Scene
from foley.schemas import FoleyError


@pytest.fixture
def engine():
    if not shutil.which(os.environ.get("FOLEY_CSOUND", "csound")):
        pytest.skip("Csound is not installed; real rendering not verified")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration", 0),
        ("duration", 61),
        ("duration", float("nan")),
        ("sample_rate", 44100),
        ("channels", 3),
        ("seed", 0),
        ("seed", -1),
        ("seed", True),
        ("seed", 1.5),
        ("layers", []),
        ("layers", [Layer().model_dump()] * 33),
        ("extra_program", "system()"),
    ],
)
def test_scene_rejects_invalid(field, value):
    data = lib.recipe("wind").model_dump()
    data[field] = value
    with pytest.raises(ValueError, match="validation error"):
        Scene.model_validate(data)


@pytest.mark.parametrize(
    "change",
    [
        {"source": "system"},
        {"frequency": '440\nsystem("touch hacked")'},
        {"frequency": float("inf")},
        {"attack": 0.9, "release": 0.9},
        {"resonance_mix": 1, "resonance": 0},
        {"pan": 2},
    ],
)
def test_layer_rejects_untrusted_program_and_ranges(change):
    with pytest.raises(ValueError, match="validation error"):
        Layer.model_validate(change)


def test_scene_rejects_out_of_bounds_timing():
    with pytest.raises(ValueError, match="end within"):
        Scene(duration=1, layers=[Layer(start=0.5, duration=1)])
    with pytest.raises(ValueError, match="crossfade"):
        Scene(duration=0.1, loop=True, crossfade_ms=30, layers=[Layer(duration=0.05, release=0.01)])


def test_compiler_uses_no_strings_as_code():
    scene = lib.recipe("wind").model_dump()
    bad = '</CsInstruments>\nsystem_i "touch hacked"\n'
    scene["title"] = bad
    scene["description"] = bad
    scene["layers"][0]["name"] = bad
    csd = compile_scene(Scene.model_validate(scene))
    assert bad not in csd
    assert "touch" not in csd
    assert csd.count("<CsInstruments>") == 1
    assert csd == compile_scene(Scene.model_validate(scene))


@pytest.mark.parametrize("recipe", lib.RECIPES)
@pytest.mark.parametrize("channels", [1, 2])
def test_real_recipes(engine, tmp_path, recipe, channels):
    scene = lib.recipe(recipe, duration=1.5, channels=channels, seed=17)
    _, report = render_audio(scene, tmp_path / "audio.wav")
    assert report["subtype"] == "PCM_24"
    assert report["frames"] == 72000
    assert report["sample_rate"] == 48000
    assert report["channels"] == channels
    assert -90 < report["rms_dbfs"] < -1
    assert report["peak_dbfs"] <= -0.999
    assert report["boundary_delta"] <= 1 / 8388608


def test_seed_reproducibility_and_variation(engine, tmp_path):
    a = lib.recipe("rain", seed=71)
    b = lib.recipe("rain", seed=72)
    _, first = render_audio(a, tmp_path / "a.wav")
    _, second = render_audio(a, tmp_path / "b.wav")
    _, third = render_audio(b, tmp_path / "c.wav")
    assert first["sha256"] == second["sha256"]
    assert first["sha256"] != third["sha256"]


def test_loop_length_and_boundary(engine, tmp_path):
    scene = lib.recipe("wind", duration=1.12345, loop=True)
    _, report = render_audio(scene, tmp_path / "loop.wav")
    assert report["frames"] == round(1.12345 * 48000)
    assert report["boundary_delta"] == 0
    assert report["loop_treatment"] == "symmetric boundary crossfade"


@pytest.mark.parametrize("fault", ["silent", "nan", "rate", "channels", "short", "missing", "malformed"])
def test_bad_audio_never_success(tmp_path, fault):
    scene = lib.recipe("wind")
    path = tmp_path / "bad.wav"
    if fault == "malformed":
        path.write_bytes(b"not a wave")
    elif fault != "missing":
        values = np.full((scene.frames, 2), 0.1)
        if fault == "silent":
            values[:] = 0
        if fault == "nan":
            values[100] = float("nan")
        if fault == "channels":
            values = values[:, 0]
        if fault == "short":
            values = values[:50]
        sf.write(path, values, 44100 if fault == "rate" else 48000, subtype="FLOAT")
    with pytest.raises(FoleyError):
        read_audio(path, scene)


def test_renderer_timeout_and_fixed_command(tmp_path, monkeypatch):
    monkeypatch.setattr("foley.audio.engine_path", lambda: "/trusted/csound")

    def timeout(command, **kwargs):
        assert command == ["/trusted/csound", "-d", "-m0", "-W", "-f", "-o", "raw.wav", "scene.csd"]
        assert kwargs["timeout"] == 90
        assert kwargs["cwd"] != tmp_path
        assert "shell" not in kwargs
        raise subprocess.TimeoutExpired(command, 90)

    monkeypatch.setattr("foley.audio.subprocess.run", timeout)
    with pytest.raises(FoleyError, match="90 seconds"):
        render_audio(lib.recipe("wind"), tmp_path / "out.wav")
    assert not (tmp_path / "out.wav").exists()


def test_deterministic_import_never_loads_agent():
    script = "import sys; from foley import lib; lib.recipe('wind'); assert 'amplifier_agent' not in sys.modules"
    import sys

    subprocess.run([sys.executable, "-c", script], check=True)


@pytest.mark.parametrize("name", lib.RECIPES)
@pytest.mark.parametrize("duration", [0.05, 0.1, 60])
def test_recipe_boundaries(name, duration):
    scene = lib.recipe(name, duration=duration, loop=True)
    assert scene.duration == duration
    assert len(scene.layers) <= 32


def test_real_impulse(engine, tmp_path):
    scene = Scene(
        duration=0.2, layers=[Layer(source="impulse", duration=0.2, resonance=400, resonance_width=80, resonance_mix=1)]
    )
    _, validation = render_audio(scene, tmp_path / "impulse.wav")
    assert validation["rms_dbfs"] > -100


@pytest.mark.parametrize("channels", [1, 2])
def test_only_noise_seed_changes_decoded_pcm(engine, tmp_path, channels):
    base = Scene(duration=0.25, channels=channels, layers=[Layer(duration=0.25, sustain=1)])
    pcm_hashes = []
    for index, seed in enumerate([1, 1, 2, 17, 2147483646]):
        scene = Scene.model_validate({**base.model_dump(), "seed": seed})
        path = tmp_path / f"noise-{index}.wav"
        render_audio(scene, path)
        samples, _ = sf.read(path, dtype="int32", always_2d=True)
        pcm_hashes.append(hashlib.sha256(samples.tobytes()).hexdigest())
    assert pcm_hashes[0] == pcm_hashes[1]
    assert len(set(pcm_hashes)) == 4


@pytest.mark.parametrize("seed", [1, 2, 2147483646])
def test_rand_seeds_are_per_layer_bounded_and_31bit(seed):
    scene = Scene(seed=seed, layers=[Layer(), Layer()])
    noise_lines = [line for line in compile_scene(scene).splitlines() if line.startswith("asrc rand ")]
    seeds = []
    for line in noise_lines:
        parts = line.removeprefix("asrc rand ").split(",")
        assert len(parts) == 3
        assert parts[0].strip() == "1"
        assert parts[2].strip() == "1"
        seeds.append(float(parts[1]))
    assert all(0 < value < 1 for value in seeds)
    assert len(set(seeds)) == 2


def test_public_rain_variants_change_noise_preserve_parent(engine, tmp_path):
    parent = lib.render(lib.recipe("rain", seed=1, duration=1), tmp_path)
    parent_dir = tmp_path / parent["id"]
    before = {p.name: p.read_bytes() for p in parent_dir.iterdir()}
    children = lib.variants(parent["id"], [2, 17], tmp_path)
    repeat = lib.variants(parent["id"], [2], tmp_path)[0]

    def pcm(revision):
        samples, _ = sf.read(tmp_path / revision["id"] / "audio.wav", dtype="int32")
        return hashlib.sha256(samples.tobytes()).hexdigest()

    assert len({pcm(item) for item in [parent, *children]}) == 3
    assert pcm(children[0]) == pcm(repeat)
    assert all(item["parent"] == parent["id"] for item in children)
    for item in children:
        for name in ("frames", "channels", "sample_rate", "subtype"):
            assert item["validation"][name] == parent["validation"][name]
    assert {p.name: p.read_bytes() for p in parent_dir.iterdir()} == before


def test_renderer_environment_excludes_credential_canaries(engine, tmp_path, monkeypatch):
    canaries = (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "COPILOT_AGENT_TOKEN",
        "COPILOT_GITHUB_TOKEN",
        "AMPLIFIER_AGENT_CONFIG",
        "UNRECOGNIZED_SECRET",
        "HTTP_PROXY",
    )
    for name in canaries:
        monkeypatch.setenv(name, "synthetic-credential-canary")
    actual_run = subprocess.run
    observed = []

    def inspect_run(command, **kwargs):
        env = kwargs["env"]
        assert not set(canaries).intersection(env)
        assert "synthetic-credential-canary" not in env.values()
        assert Path(env["HOME"]) == kwargs["cwd"]
        assert env.get("LD_LIBRARY_PATH") == os.environ.get("LD_LIBRARY_PATH")
        observed.append(True)
        return actual_run(command, **kwargs)

    monkeypatch.setattr("foley.audio.subprocess.run", inspect_run)
    render_audio(lib.recipe("wind", duration=0.25), tmp_path / "canary.wav")
    assert observed == [True]


@pytest.mark.parametrize(("sustain", "release"), [(0, 0.1), (0, 0.8), (0.5, 0.1), (0.5, 0.8)])
def test_envelope_semantics_in_decoded_pcm(engine, tmp_path, sustain, release):
    """Measure AC support, not DC padding or names suggesting an audible tail."""
    layer = Layer(
        source="sine",
        start=0.05,
        duration=1,
        attack=0.01,
        release=release,
        sustain=sustain,
        frequency=1000,
        frequency_end=1000,
        gain_db=-12,
    )
    scene = Scene(duration=1.2, channels=1, layers=[layer])
    path = tmp_path / "envelope.wav"
    render_audio(scene, path)
    samples, rate = sf.read(path, dtype="float64")
    bins = samples.reshape(-1, 480)
    ac = bins - bins.mean(axis=1, keepdims=True)
    rms = np.sqrt(np.mean(ac**2, axis=1))
    active = np.flatnonzero(rms > 1e-4)
    assert len(active) > 0
    measured_end = (int(active[-1]) + 1) * 480 / rate
    expected_end = layer.start + layer.duration - (release if sustain == 0 else 0)
    assert measured_end == pytest.approx(expected_end, abs=0.02)
    middle = samples[round(0.4 * rate) : round(0.6 * rate)]
    middle_ac_rms = float(np.std(middle))
    if sustain == 0 and release == 0.8:
        assert middle_ac_rms < 1e-7
    else:
        assert middle_ac_rms > 0.005
    after = samples[round((expected_end + 0.01) * rate) : round(1.18 * rate)]
    assert float(np.std(after)) < 1e-7


def test_envelope_descriptions_define_existing_semantics():
    properties = Layer.model_json_schema()["properties"]
    assert "includes attack, middle ramp and release" in properties["duration"]["description"]
    assert "0 to 1" in properties["attack"]["description"]
    assert "sustain to 0" in properties["release"]["description"]
    assert "level at release start" in properties["sustain"]["description"]
    assert "sustain=0 makes release silent" in properties["sustain"]["description"]
    assert properties["sustain"]["minimum"] == 0
    assert Layer(sustain=0).sustain == 0
