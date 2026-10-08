# Foley Smart Tool

Design, audition, revise, and export production sound effects with Csound and Amplifier Agent.

Foley is a [Smart Tool](https://github.com/microsoft/amplifier-smart-tools): a library with a thin CLI over it, whose model-backed capabilities sit behind an interface.

## Installation

Prerequisites:
- [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Python 3.13+ (uv can manage it).
- [Csound 6.18+](https://csound.com/download.html) on PATH for rendering. On Debian/Ubuntu:
  `sudo apt install csound`; on macOS: `brew install csound`; on Windows use the
  official installer and add its executable directory to PATH. These are user-run
  installation examples, not commands Foley executes.
- For natural-language design only: one supported provider's credentials.
  OpenAI uses OPENAI_API_KEY, Anthropic uses ANTHROPIC_API_KEY, Gemini uses
  GOOGLE_API_KEY or GEMINI_API_KEY. GitHub Copilot uses an entitled account and
  `gh auth login` or its supported token environment. ChatGPT uses separate
  [Amplifier Agent OAuth login](https://github.com/microsoft/amplifier-agent/blob/v0.22.0/docs/providers.md).
  Foley never initiates interactive login.

```bash
uv tool install git+https://github.com/robotdad/amplifier-smart-tool-foley@main
```

To use it as a library:

```bash
uv add "foley @ git+https://github.com/robotdad/amplifier-smart-tool-foley"
```

To run it once without installing:

```bash
uvx --from git+https://github.com/robotdad/amplifier-smart-tool-foley foley --help
```

To teach a coding agent how to use it, install the [skill](skills/foley/SKILL.md):

```bash
npx skills add robotdad/amplifier-smart-tool-foley
```

To update:

```bash
uv tool upgrade foley
npx skills update foley   # add --global if the skill was installed globally
```

To uninstall:

```bash
uv tool uninstall foley
npx skills remove foley   # add --global if the skill was installed globally
```

Verify an install with `foley manifest`, which needs no credentials.

## Interface

```bash
foley doctor --providers
foley create "Three heavy boots on a hollow wooden floor, with tiny creaks" \
  --duration 2 --provider openai --model gpt-6-astra --store ./sounds
```

Copy the returned `id` into these commands:

```bash
foley audition REVISION --destination listen.html --store ./sounds
foley revise REVISION "Make the boots lighter and add a longer creak" \
  --duration 3 --provider openai --model gpt-6-astra --store ./sounds
foley audition ORIGINAL CHILD --destination compare.html --store ./sounds
foley export CHILD footsteps.wav --store ./sounds
foley export CHILD footsteps.zip --bundle --store ./sounds
```

Open the HTML locally to listen and download. It embeds the actual audio and needs
no server, internet connection or model access. Use new destination names; files
are never overwritten. The interface is deliberately small: your agent drives
creation and revisions, and the browser is the listening/comparison surface.

No credentials? Use the same renderer with deterministic editable scenes:

```bash
foley recipe --name metal-impact --duration 2 --seed 17 > metal.json
foley render metal.json --store ./sounds
foley variants REVISION --seed 41 --seed 42 --store ./sounds
foley list --store ./sounds
```

See the [CLI reference](docs/02-cli.md) for every flag and the [library reference](docs/01-library.md) for the Python surface.

## Intelligence and delivery

Public Amplifier Agent 0.22.0 is the only intelligence implementation. Supported
provider IDs are `openai`, `anthropic`, `gemini`, `openai-chatgpt` and `github-copilot`.
Use `foley models --provider NAME` to discover exact model IDs. Explicit models are
never substituted. When omitted, models default from the single schemas.py map:
gpt-6-astra for OpenAI/ChatGPT/GitHub, claude-sonnet-5-5 for Anthropic, and
gemini-3.8-flash for Gemini. Account availability is not guaranteed. Default effort
is medium, configurable.

The model submits bounded numeric scene data, never executable Csound. Only a
scene-submission tool is supplied; no shell, filesystem, skills or MCP servers.
Agent runs use a private working/config/session directory, with no inherited
capture destinations or request overrides. Credentials stay in process environment
or supported account caches and are not copied to exported artifacts.

Each revision retains original brief, change request, parent, scene, seed, compiled
CSD, 48 kHz / 24-bit mono/stereo WAV, checksums, audio measurements and reported
provider/model/usage. Failed renders cannot replace existing sounds. Exports are
plain WAV or reproducible audit ZIP. Loop boundary treatment preserves duration.

These are procedural effects, not a claim of indistinguishable recorded foley.
The model receives no audio and cannot listen. Waveform checks establish format,
non-silence and headroom, not artistic quality or a perceptually seamless loop.
Same-engine seeded rendering is reproducible; cross-version/platform byte identity
is not promised. Linux is locally exercised; macOS/Windows instructions are not
platform verification. No live provider success is claimed by offline tests.

## Initial validation and known limits

The initial Linux arm64 build passed 131 source tests, 130 installed tests and
16 Smart Tool conformance checks in a Digital Twin Universe environment.
Live creation produced retained audio through OpenAI, Anthropic, Gemini and
GitHub Copilot. ChatGPT's adapter is implemented, but its separate OAuth login
was unavailable for a live trial. Browser checks exercised playback, seeking,
exact WAV downloads and offline reopening of the retained examples.

These checks do not establish sound quality. Two requested outcomes remain unmet:

- A shorter metal-impact revision preserved its original, but did not measurably
  reduce the post-impact ringing, including after authoring-guidance improvements.
- A ventilation loop had matching endpoint samples but a roughly 20.6 dB,
  20 ms volume dip around the join. Loop playback works; seamless ambience is
  not established.

An independent audio evaluator failed simple control cases, so no automated
listening verdict is claimed. Audition outputs before production use.
The [draft-clause evidence](docs/clause-evidence.md) separates checks from promises;
the vision and contracts remain drafts, not ratified acceptance.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your development environment.

## License

MIT; see [LICENSE](LICENSE). Scaffold portions derive from Microsoft's
[Smart Tool Creator](https://github.com/microsoft/amplifier-smart-tool-creator).
Csound is a separately installed dependency under its own LGPL license.
