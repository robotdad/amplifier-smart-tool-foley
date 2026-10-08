"""Useful starting points, not limits on the composable scene language."""

import random

from foley.scene import Layer, Scene
from foley.schemas import FoleyError

RECIPES = ("wood-impact", "metal-impact", "footsteps", "whoosh", "laser", "interface", "rain", "wind", "machinery")


def recipe(name: str, duration: float = 2, seed: int = 1, channels: int = 2, loop: bool = False) -> Scene:
    if name not in RECIPES:
        raise FoleyError(f"Unknown recipe. Choose {', '.join(RECIPES)}.")
    randomizer = random.Random(seed)
    layers: list[Layer] = []

    def layer(**kwargs) -> None:
        length = kwargs.get("duration", duration)
        layers.append(
            Layer.model_validate(
                {
                    "duration": length,
                    "attack": min(0.005, length / 4),
                    "release": min(0.15, length / 3),
                    **kwargs,
                }
            )
        )

    if name in {"wood-impact", "metal-impact", "footsteps"}:
        times = [0] if name != "footsteps" else [i * 0.45 for i in range(min(8, max(1, int(duration / 0.45))))]
        for i, start in enumerate(times):
            length = min(duration - start, 1.4 if name == "metal-impact" else 0.35)
            layer(
                name=f"contact {i + 1}",
                source="noise",
                start=start,
                duration=min(length, 0.08),
                gain_db=-8,
                cutoff=6000,
                cutoff_end=600,
                sustain=0.05,
                pan=(-0.25 if i % 2 else 0.25),
            )
            for j, frequency in enumerate([180, 347, 621] if name != "metal-impact" else [623, 1021, 1749, 2833]):
                frequency *= randomizer.uniform(0.96, 1.04)
                layer(
                    name=f"material {i + 1}-{j + 1}",
                    source="sine",
                    start=start,
                    duration=length,
                    frequency=frequency,
                    frequency_end=frequency * 0.98,
                    gain_db=-12 - j * 3,
                    release=length * 0.8,
                    sustain=0.15,
                )
    elif name == "whoosh":
        layer(
            name="air motion",
            cutoff=250,
            cutoff_end=12000,
            highpass=180,
            attack=duration * 0.55,
            release=duration * 0.4,
            pan=-0.9,
            pan_end=0.9,
            gain_db=-7,
        )
        layer(
            name="low body",
            source="sine",
            frequency=160,
            frequency_end=45,
            attack=duration * 0.5,
            release=duration * 0.45,
            gain_db=-18,
        )
    elif name in {"laser", "interface"}:
        layer(
            name="pitch gesture",
            source="sine",
            frequency=1800 if name == "laser" else 660,
            frequency_end=60 if name == "laser" else 1320,
            gain_db=-10,
            modulation_hz=32 if name == "laser" else 5,
            modulation_depth=0.3,
            release=duration * 0.8,
        )
        layer(
            name="harmonic edge",
            source="triangle",
            frequency=2500,
            frequency_end=180,
            gain_db=-25,
            release=duration * 0.8,
        )
    elif name == "rain":
        layer(
            name="rain bed",
            gain_db=-18,
            cutoff=12000,
            highpass=1000,
            attack=min(duration / 4, 0.1),
            release=min(duration / 4, 0.1),
            sustain=1,
        )
        for i in range(8):
            start = duration * i / 9
            layer(
                name=f"drop {i + 1}",
                start=start,
                duration=max(0.01, min(0.08, duration / 8)),
                gain_db=-19,
                cutoff=randomizer.uniform(2000, 12000),
                resonance=1800 + i * 197,
                resonance_width=80,
                resonance_mix=0.7,
                pan=randomizer.uniform(-1, 1),
            )
    elif name == "wind":
        layer(
            name="wind bed",
            gain_db=-8,
            cutoff=500,
            cutoff_end=1800,
            highpass=40,
            sustain=1,
            attack=duration * 0.2,
            release=duration * 0.2,
            modulation_hz=0.4,
            modulation_depth=0.8,
        )
        layer(
            name="air whistle",
            source="sine",
            frequency=480,
            frequency_end=370,
            gain_db=-30,
            modulation_hz=0.7,
            modulation_depth=0.8,
            attack=duration * 0.3,
            release=duration * 0.3,
        )
    else:
        layer(
            name="motor",
            source="triangle",
            frequency=65,
            frequency_end=72,
            gain_db=-17,
            sustain=1,
            modulation_hz=11,
            modulation_depth=0.4,
        )
        layer(
            name="rattle",
            cutoff=2400,
            gain_db=-20,
            sustain=1,
            modulation_hz=17,
            modulation_depth=0.9,
            resonance=730,
            resonance_mix=0.7,
        )
    return Scene.model_validate(
        {
            "title": name.replace("-", " ").title(),
            "description": f"Deterministic {name} synthesis starting point.",
            "duration": duration,
            "seed": seed,
            "channels": channels,
            "loop": loop,
            "crossfade_ms": min(20, duration * 250),
            "layers": [item.model_dump() for item in layers],
        }
    )
