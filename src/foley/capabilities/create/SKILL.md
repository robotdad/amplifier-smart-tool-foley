# Create a sound

Model-backed through public Amplifier Agent. BRIEF describes material, action,
timing, texture and production use. Produces real Csound audio, not arbitrary CSD.

```bash
foley create "Heavy wooden door slams, short hollow body and tiny latch rattle" \
  --provider openai --model gpt-6-astra --duration 2 --seed 17 --store ./sounds
```

Options: `--store` library path (default FOLEY_HOME or ~/.local/share/foley);
`--provider` openai, anthropic, gemini, openai-chatgpt or github-copilot
(aliases chatgpt/github); `--model` exact provider model ID, default from schemas;
`--duration` 0.05-60 seconds (default 2); `--channels` 1 or 2 (default 2);
`--seed` 1-2147483646; `--loop` / `--no-loop` boundary crossfade (default off);
`--reasoning-effort` none/minimal/low/medium/high/xhigh/max (default medium);
`--timeout` model operation seconds (default 300).

Returns JSON with id, parent, original_brief, scene, seed, intelligence provenance,
audio SHA256 and actual validation measurements. Use the id with audition/revise/export.
Provider/model are never silently substituted. Use `foley models --provider NAME`
for supported IDs. Omitted models use the schemas.py provider default:
OpenAI/ChatGPT/GitHub gpt-6-astra, Anthropic claude-sonnet-5-5, Gemini gemini-3.8-flash.

Failures: invalid input, missing Csound, credentials/model refusal, no valid
submission, render timeout, malformed or silent audio. No revision is published on
failure. A validated submission may be rendered when the model's subsequent closing
message fails; its terminal_state remains in provenance. No automatic retry/login.
No audio is sent to the model; it cannot claim listening-based review.