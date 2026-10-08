# Deliver a production asset

```bash
foley export REVISION effect.wav --store ./sounds
foley export REVISION effect.zip --bundle --store ./sounds
```

REVISION exact id; DESTINATION caller-owned new path outside the source library.
`--bundle` / `--no-bundle` selects deterministic audit ZIP or WAV (default);
`--store` chooses the library. WAV is 48 kHz / 24-bit with original channels.
ZIP contains audio.wav, scene.json, scene.csd, revision.json and hashes.json.
Fixed ZIP timestamps make repeated exports byte-identical.

Returns destination path, size and SHA256. No model or Csound needed. Parent IDs
are references, not copies of all ancestors. Missing/corrupt revisions, source
library destinations and existing output files are refused. Choose a fresh name;
exports never overwrite. A write error may leave an incomplete caller destination.