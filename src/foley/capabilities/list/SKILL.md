# List sounds

```bash
foley list --store ./sounds
```

`--store` optional library location. Returns a JSON list of retained revisions,
including exact parent IDs, briefs, scenes, provenance and validation. An absent
library returns an empty list. No model or Csound needed. Invalid or modified
retained files fail integrity verification, never silently disappear from the list.