# Discover exact model IDs

```bash
foley models --provider anthropic
```

`--provider` openai (default), anthropic, gemini, openai-chatgpt or github-copilot;
chatgpt/github aliases accepted. Uses public Amplifier Agent list_models and may
query provider catalogs, but never generates content or starts login.
Returns model IDs, capabilities and supported effort values where reported.
Missing credentials, unavailable extra or provider catalog errors return an error.
Select one exact ID with create/revise --model; Foley does not silently switch.