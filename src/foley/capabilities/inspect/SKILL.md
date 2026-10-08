# Inspect a revision

```bash
foley inspect REVISION --store ./sounds
```

REVISION is an exact 32-character id, not a path. `--store` chooses the library.
Returns JSON metadata, full numeric scene, original brief, change request, parent,
seed, model provenance and actual waveform measurements. Verifies all retained
payload hashes. Does not synthesize or call a model.
Missing IDs, traversal strings, symlinked files or changed hashes fail with a remedy.
Checksums detect accidental changes; they are not signatures against a hostile
same-user process with write access to the whole library.