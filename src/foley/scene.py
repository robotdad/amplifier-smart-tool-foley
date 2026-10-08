"""Bounded, composable data, never an executable synthesis language."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, frozen=True)


class Layer(ValueModel):
    """One timed excitation, moving filter and optional material resonance."""

    name: str = Field(default="layer", min_length=1, max_length=100)
    source: Literal["noise", "sine", "triangle", "impulse"] = "noise"
    start: float = Field(default=0, ge=0, le=60)
    duration: float = Field(
        default=1,
        ge=0.01,
        le=60,
        description=(
            "Scheduled layer length in seconds; includes attack, middle ramp and release, not an added tail. "
            "Envelope: 0 -> 1 over attack, 1 -> sustain over max(duration-attack-release, 1e-8), "
            "then sustain -> 0 over release. The middle is a linear ramp, not a hold. "
            "Playback stops at start+duration."
        ),
    )
    gain_db: float = Field(default=-12, ge=-60, le=0)
    attack: float = Field(
        default=0.005,
        ge=0.0001,
        le=60,
        description="Seconds for the linear amplitude rise from 0 to 1 at layer start. Included in duration; attack+release must fit duration.",
    )
    release: float = Field(
        default=0.1,
        ge=0.0001,
        le=60,
        description=(
            "Seconds for the final linear amplitude ramp from sustain to 0, included in duration. "
            "sustain=0 makes release silent (0 -> 0), even with a long release. "
            "A long decaying release needs a positive sustain level at its start. "
            "Alternatively a long middle ramp to sustain=0 with a short release creates decay before release."
        ),
    )
    sustain: float = Field(
        default=0.7,
        ge=0,
        le=1,
        description=(
            "Amplitude level at release start (0..1), not a duration or guaranteed held plateau. "
            "The middle ramp falls from 1 to this level; release ramps from this level to 0. "
            "sustain=0 makes release silent; positive support then ends at "
            "start+attack+max(duration-attack-release, 1e-8), capped by start+duration. "
            "Zero is valid for a transient or middle-ramp decay. Filters/resonators are before this "
            "output envelope, so it also gates their tails."
        ),
    )
    frequency: float = Field(default=440, ge=20, le=18000)
    frequency_end: float = Field(default=440, ge=20, le=18000)
    cutoff: float = Field(default=8000, ge=40, le=20000)
    cutoff_end: float = Field(default=8000, ge=40, le=20000)
    highpass: float = Field(default=30, ge=20, le=18000)
    resonance: float = Field(default=0, ge=0, le=18000)
    resonance_width: float = Field(default=100, ge=20, le=4000)
    resonance_mix: float = Field(default=0, ge=0, le=1)
    modulation_hz: float = Field(default=0, ge=0, le=100)
    modulation_depth: float = Field(default=0, ge=0, le=1)
    pan: float = Field(default=0, ge=-1, le=1)
    pan_end: float = Field(default=0, ge=-1, le=1)

    @model_validator(mode="after")
    def envelope_fits(self) -> Self:
        if self.attack + self.release > self.duration:
            raise ValueError("attack + release must fit layer duration")
        if self.resonance_mix and self.resonance < 20:
            raise ValueError("a resonant layer needs resonance >= 20 Hz")
        return self


class Scene(ValueModel):
    schema_version: Literal[1] = 1
    title: str = Field(default="Untitled sound", min_length=1, max_length=160)
    description: str = Field(default="", max_length=4000)
    duration: float = Field(default=2, ge=0.05, le=60)
    sample_rate: Literal[48000] = 48000
    channels: Literal[1, 2] = 2
    seed: int = Field(default=1, ge=1, le=2147483646, strict=True)
    loop: bool = False
    crossfade_ms: float = Field(default=20, ge=1, le=250)
    layers: list[Layer] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def timing_fits(self) -> Self:
        if any(layer.start + layer.duration > self.duration + 1e-8 for layer in self.layers):
            raise ValueError("every layer must end within scene duration")
        if self.loop and self.crossfade_ms / 1000 > self.duration / 4:
            raise ValueError("loop crossfade must be at most one quarter of duration")
        return self

    @property
    def frames(self) -> int:
        return round(self.duration * self.sample_rate)
