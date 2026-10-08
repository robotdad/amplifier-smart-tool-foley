# Revise an exact sound

REVISION is a retained 32-character ID. CHANGES describes what should change.
The actual prior scene is supplied to public Amplifier Agent. The original remains intact.

```bash
foley revise REVISION "Make the impact softer, and extend the wooden creak" \
  --duration 3 --provider openai --model gpt-6-astra --store ./sounds
```

Options: `--store` chooses the library; `--provider` and `--model` explicitly
select intelligence, never silently changed; `--duration` changes duration or
defaults to the original; `--reasoning-effort` defaults medium; `--timeout` defaults
300 seconds. Channels, seed and loop setting carry forward. Duration is not immutable.

Returns a new id and exact parent with original_brief and change_request preserved,
new audio, scene, source, hashes and provider usage where available. Use both IDs with
audition to compare. Failures preserve the parent and publish no child.
Missing revision, malformed scene, unavailable credentials/model, no submission and
failed/silent rendering name remedies. No model audio listening or implicit login.