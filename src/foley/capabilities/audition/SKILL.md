# Audition and compare

```bash
foley audition ORIGINAL CHILD --destination compare.html --store ./sounds
```

REVISIONS is one to eight retained IDs in display order. `--destination` required
new HTML filename outside the source library; `--store` library location.
Returns path, size and selected IDs. Open the file in a modern browser. Native
audio controls support playback and seeking; download links deliver actual WAVs.
Cards show briefs, change requests, parents, seeds and measured properties.
Audio is embedded. There is no CDN, server, model call, autoplay or telemetry.

Comparison is human listening, not AI judgment or synchronized A/B playback.
This view is read-only; tell your agent the revision ID and changes to request.
Missing/corrupt IDs, more than eight sounds, >100 MB source audio or an existing
destination fail. HTML escapes all supplied text and blocks scripts/network access.