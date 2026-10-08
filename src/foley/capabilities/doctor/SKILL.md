# Readiness without generation

```bash
foley doctor --providers
```

`--providers` / `--no-providers` optionally asks public Amplifier Agent for
installed and credential status for all five providers. Default checks only local
Csound/version readiness; no Agent import. Returns JSON and no paid generation.
render_ready means the executable answered --version, not a successful audio trial.

Install Csound 6.18+ from https://csound.com/download.html or your OS package
manager. Put csound on PATH, or set FOLEY_CSOUND to a trusted executable.
API auth: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY or GEMINI_API_KEY.
GitHub: an entitled Copilot account through gh auth login or supported token env.
ChatGPT: complete Amplifier Agent's separate OAuth login before using Foley.
No implicit interactive login. Never paste credentials into a brief or scene.
Found credentials are not proof of entitlement or live generation.