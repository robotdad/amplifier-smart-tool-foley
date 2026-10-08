# Render scene data

```bash
foley render metal.json --brief "Metal tray dropped on tile" --store ./sounds
```

SCENE_FILE is a JSON scene (up to 1 MB). `--brief` optional original brief;
`--store` optional library location. Returns an immutable revision with id, scene,
Csound source, 48 kHz / 24-bit PCM WAV, SHA256 and audio measurements.

No intelligence is imported or credentials required. Csound 6.18+ must be on PATH;
FOLEY_CSOUND can name an explicitly trusted executable. Rendering runs in a private
temporary directory with fixed arguments and 90-second timeout. No user CSD, shell
commands, file paths or opcodes are accepted inside scenes.

Peak attenuation only, at -1 dBFS ceiling; never boosts quiet synthesis. Removes DC.
Non-looping audio receives 5 ms edge fades. Loop mode uses a symmetric boundary
crossfade without changing duration, not a guarantee of perceptually seamless
ambience. Inspect and audition the result.

Invalid scene/envelope/timing, missing Csound, timeout, wrong sample rate/channels/
duration, malformed/non-finite/silent output all fail without publishing a revision.