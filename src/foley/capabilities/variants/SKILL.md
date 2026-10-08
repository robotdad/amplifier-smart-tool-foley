# Seeded variations

```bash
foley variants REVISION --seed 41 --seed 42 --store ./sounds
```

REVISION is the exact retained parent. Repeat `--seed` one to eight times with
distinct integer seeds 1-2147483646. `--store` chooses the library.
Returns a list of independently retained children. Each changes seeded noise and
applies up to 4% seeded pitch jitter; it is not a model call. Original audio remains
unchanged. Same seeds and parent reproduce the same audio with the same engine.

All seeds validate before rendering. If a later child fails, earlier published
children remain discoverable with list; do not assume batch atomicity or retry the
whole batch blindly. Csound and all render validation rules apply.