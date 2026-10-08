# Foley Smart Tool

Design, audition, revise, and export production sound effects with Csound and Amplifier Agent.

Foley is a [Smart Tool](https://github.com/microsoft/amplifier-smart-tools): a library with a thin CLI over it, whose model-backed capabilities sit behind an interface.

## Installation

Prerequisites:
- [uv](https://docs.astral.sh/uv/getting-started/installation/).
- [GitHub CLI](https://cli.github.com/) signed in to an account with a [GitHub Copilot subscription](https://github.com/github/copilot-cli#prerequisites) for the model-backed capabilities.

```bash
uv tool install git+https://github.com/robotdad/amplifier-smart-tool-foley
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
# Print the tool's manifest as JSON
foley manifest
```

See the [CLI reference](docs/02-cli.md) for every flag and the [library reference](docs/01-library.md) for the Python surface.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your development environment.
