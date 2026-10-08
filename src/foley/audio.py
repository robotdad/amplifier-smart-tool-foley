"""Trusted numeric Csound compiler and validated PCM delivery."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

import numpy as np
import soundfile as sf

from foley.scene import Scene
from foley.schemas import FoleyError

RENDER_ENV_PATHS = (
    "PATH",
    "SystemRoot",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "LD_LIBRARY_PATH",
    "DYLD_LIBRARY_PATH",
    "DYLD_FALLBACK_LIBRARY_PATH",
    "OPCODE6DIR",
    "OPCODE6DIR64",
)


def renderer_environment(root: Path) -> dict[str, str]:
    """Retain only trusted executable/library paths; isolate config and temp files."""
    environment = {key: os.environ[key] for key in RENDER_ENV_PATHS if key in os.environ}
    environment.update({key: str(root) for key in ("HOME", "USERPROFILE", "XDG_CONFIG_HOME", "TMPDIR", "TMP", "TEMP")})
    environment["LC_ALL"] = "C"
    return environment


def engine_path() -> str:
    requested = os.environ.get("FOLEY_CSOUND", "csound")
    resolved = shutil.which(requested)
    if not resolved:
        raise FoleyError("Csound is missing. Install Csound 6.18+ and put csound on PATH, or set FOLEY_CSOUND.")
    return str(Path(resolved).resolve())


def compile_scene(scene: Scene) -> str:
    """Text metadata never enters CSD; all expressions originate in this compiler."""
    scene = Scene.model_validate(scene.model_dump())
    lines = [
        "<CsoundSynthesizer>",
        "<CsOptions>",
        "</CsOptions>",
        "<CsInstruments>",
        "sr = 48000",
        "ksmps = 1",
        f"nchnls = {scene.channels}",
        "0dbfs = 1",
        f"seed {scene.seed}",
    ]
    score = []
    for i, layer in enumerate(scene.layers, 1):
        lines += [
            f"instr {i}",
            f"kfreq line {layer.frequency}, p3, {layer.frequency_end}",
            f"kcut line {layer.cutoff}, p3, {layer.cutoff_end}",
            f"kpan line {(layer.pan + 1) / 2}, p3, {(layer.pan_end + 1) / 2}",
        ]
        if layer.source == "noise":
            # rand ignores global seed. Its own seed must be in (0, 1) or it
            # switches to clock seeding; isel=1 selects the 31-bit generator.
            seed = ((scene.seed - 1 + (i - 1) * 104729) % 2147483646 + 1) / 2147483647
            lines.append(f"asrc rand 1, {seed:.17g}, 1")
        elif layer.source == "impulse":
            lines.append("asrc mpulse 1, 0")
        elif layer.source == "triangle":
            lines.append("asrc vco2 0.5, kfreq, 12")
        else:
            lines.append("asrc oscili 1, kfreq")
        lines += [f"ahigh butterhp asrc, {layer.highpass}", "afilt butterlp ahigh, kcut"]
        if layer.resonance_mix:
            lines += [
                f"ares reson afilt, {layer.resonance}, {layer.resonance_width}, 1",
                f"afilt = afilt * {1 - layer.resonance_mix} + ares * {layer.resonance_mix}",
            ]
        hold = max(layer.duration - layer.attack - layer.release, 0.00000001)
        lines += [
            f"aenv linseg 0, {layer.attack}, 1, {hold}, {layer.sustain}, {layer.release}, 0",
            f"amod oscili {layer.modulation_depth / 2}, {max(layer.modulation_hz, 0.001)}",
            f"asig = afilt * aenv * {10 ** (layer.gain_db / 20)} * (1 - {layer.modulation_depth / 2} + amod)",
        ]
        if scene.channels == 2:
            lines += ["aleft, aright pan2 asig, kpan", "outs aleft, aright"]
        else:
            lines.append("out asig")
        lines.append("endin")
        score.append(f"i {i} {layer.start:.10f} {layer.duration:.10f}")
    lines += [
        "</CsInstruments>",
        "<CsScore>",
        *score,
        f"f 0 {scene.frames / 48000:.10f}",
        "e",
        "</CsScore>",
        "</CsoundSynthesizer>",
    ]
    return "\n".join(lines) + "\n"


def read_audio(path: Path, scene: Scene) -> np.ndarray:
    try:
        info = sf.info(path)
        if info.samplerate != 48000 or info.channels != scene.channels:
            raise FoleyError("Renderer returned incorrect sample rate or channel count; no revision published.")
        if abs(info.frames - scene.frames) > 1:
            raise FoleyError("Renderer returned incorrect duration; no revision published.")
        samples, _ = sf.read(path, dtype="float64", always_2d=True)
    except (RuntimeError, ValueError, OSError) as exc:
        raise FoleyError("Renderer returned malformed or missing audio; verify the Csound installation.") from exc
    if not np.isfinite(samples).all():
        raise FoleyError("Renderer returned non-finite audio; no revision published.")
    if np.max(np.abs(samples), initial=0) < 1e-7 or np.sqrt(np.mean(samples**2)) < 1e-8:
        raise FoleyError("Renderer returned silent audio; increase excitation or change the scene.")
    if len(samples) < scene.frames:
        samples = np.pad(samples, ((0, scene.frames - len(samples)), (0, 0)))
    return samples[: scene.frames]


def render_audio(scene: Scene, destination: Path) -> tuple[str, dict[str, Any]]:
    executable = engine_path()
    csd = compile_scene(scene)
    with tempfile.TemporaryDirectory(prefix="foley-render-") as directory:
        root = Path(directory)
        (root / "scene.csd").write_text(csd, encoding="utf-8")
        try:
            result = subprocess.run(
                [executable, "-d", "-m0", "-W", "-f", "-o", "raw.wav", "scene.csd"],
                cwd=root,
                env=renderer_environment(root),
                capture_output=True,
                timeout=90,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise FoleyError(
                "Csound could not complete within 90 seconds. Check doctor or simplify the scene."
            ) from exc
        if result.returncode != 0:
            raise FoleyError("Csound rejected the compiled scene; no revision published. Check engine compatibility.")
        samples = read_audio(root / "raw.wav", scene)
    raw_peak = float(np.max(np.abs(samples)))
    samples -= np.mean(samples, axis=0)
    count = min(round(scene.crossfade_ms * 48), len(samples) // 4)
    if scene.loop:
        # Symmetric boundary crossfade keeps duration and reaches the same endpoint
        # from both sides. It is boundary treatment, not proof of perceptual looping.
        head = samples[:count].copy()
        tail = samples[-count:][::-1].copy()
        common = (head + tail) / 2
        weight = (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, count)))[:, None]
        samples[:count] = head * (1 - weight) + common * weight
        samples[-count:] = (tail * (1 - weight) + common * weight)[::-1]
    else:
        count = min(240, len(samples) // 4)
        fade = np.linspace(0, 1, count)[:, None]
        samples[:count] *= fade
        samples[-count:] *= fade[::-1]
    peak = float(np.max(np.abs(samples)))
    if peak < 1e-7:
        raise FoleyError("Audio became silent after boundary treatment; change the scene.")
    gain = min(1.0, 10 ** (-1 / 20) / peak)
    samples *= gain
    sf.write(destination, samples, 48000, subtype="PCM_24", format="WAV")
    actual = read_audio(destination, scene)
    info = sf.info(destination)
    return csd, {
        "sample_rate": info.samplerate,
        "channels": info.channels,
        "frames": info.frames,
        "duration": info.frames / info.samplerate,
        "subtype": info.subtype,
        "peak_dbfs": float(20 * np.log10(np.max(np.abs(actual)))),
        "rms_dbfs": float(20 * np.log10(np.sqrt(np.mean(actual**2)))),
        "raw_peak": raw_peak,
        "attenuation_db": float(20 * np.log10(gain)),
        "boundary_delta": float(np.max(np.abs(actual[0] - actual[-1]))),
        "loop_treatment": "symmetric boundary crossfade" if scene.loop else "5 ms edge fades",
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "engine": "Csound",
        "compiler_version": 2,
    }
