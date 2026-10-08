# Make a deterministic scene

```bash
foley recipe --name metal-impact --duration 2 --seed 17 > metal.json
foley render metal.json --store ./sounds
```

Options: `--name` wood-impact (default), metal-impact, footsteps, whoosh, laser,
interface, rain, wind or machinery; `--duration` 0.05-60 seconds; `--seed`
1-2147483646; `--channels` 1 or 2; `--loop` / `--no-loop`.
Returns editable scene JSON, not rendered audio. No credentials or Csound needed.

These are starting points, not a closed list of sounds. Combine up to 32 layers:
noise/sine/triangle/impulse sources, timing, gain, envelope, pitch sweep, moving
low-pass cutoff, high-pass, resonator, amplitude modulation and stereo pan.
See `foley.scene.Scene.model_json_schema()` for exact fields and limits.
Sample rate is 48000. Layer start+duration must fit the scene; attack+release must
fit each layer. Strings are metadata and never become Csound expressions.
Invalid recipe name or values fail rather than silently clamp caller constraints.