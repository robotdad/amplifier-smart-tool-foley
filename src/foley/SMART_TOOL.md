---
smart_tool_format: 1
name: foley
version: 0.1.0
description: >-
  Design, audition, revise, and export production sound effects with Csound and Amplifier Agent
use_cases:
  - >-
    Design, audition, revise, and export production sound effects with Csound and Amplifier Agent
platforms:
  - linux
  - macos
  - windows
requires:
  - name: csound
    purpose: >-
      Synthesizes validated scenes into production WAV files. Required for render,
      create, revise and variants; not for inspecting or exporting retained sounds.
    optional: false
    install: https://csound.com/download.html
  - name: model-provider-credentials
    purpose: >-
      One supported Amplifier Agent provider account for natural-language creation
      and revision. Deterministic capabilities do not require credentials.
    optional: true
    install: https://github.com/microsoft/amplifier-agent/blob/v0.22.0/docs/providers.md
---

Design, audition, revise, and export production sound effects with Csound and Amplifier Agent.

**The library is the tool.** `foley.lib` holds every capability. The CLI is a thin
wrapper over it, so anything you can do from the shell you can also do from Python.

## When to reach for it

- Design, audition, revise, and export production sound effects with Csound and Amplifier Agent.

## Before writing code

Every capability has its own skill. Read `foley <command> --help` before calling it: it
carries the arguments, a worked invocation, the result, and the failures. Do not fill gaps
from memory. The library source beside this file, `lib.py`, carries the signatures. The
repository's `docs/01-library.md` and `docs/02-cli.md` carry the rest.

## Install

```bash
# as a CLI
uv tool install git+https://github.com/robotdad/amplifier-smart-tool-foley@main

# as a library, from another project
uv add "foley @ git+https://github.com/robotdad/amplifier-smart-tool-foley"

# once, without installing
uvx --from git+https://github.com/robotdad/amplifier-smart-tool-foley foley --help
```
Verify with `foley manifest`, which needs no credentials.

## Prerequisites

Csound 6.18+ on PATH is required for synthesis. FOLEY_CSOUND may select a trusted
executable. `doctor` checks local readiness; `doctor --providers` checks public
Amplifier Agent provider configuration without generating content.

OpenAI, Anthropic, Gemini, ChatGPT and GitHub Copilot are supported through public
Amplifier Agent. Choose both provider and exact model ID. Credentials remain outside
scenes and artifacts. Missing auth never triggers login or deterministic substitution.
Linux is locally exercised; other platform installation instructions are unverified.

## Straight and smart paths

Deterministic capabilities run with no provider configured. Create/revise are
model-backed and say so. Start with create -> audition -> revise -> audition both
IDs -> export. Use recipe -> render without credentials. Inspect and list retain
lineage; variants makes seeded alternatives. No arbitrary CSD is accepted, no audio
is sent to the model, and measured waveform validity is not listening review.

## Output and failure contract

Results go to stdout, diagnostics to stderr. A failure prints a message naming what went
wrong and how to fix it, and exits non-zero: 1 for a failure the tool can name, 2 for a
bad invocation. Never treat an empty result as success.

## Choosing a surface

Import the library from Python. Shell out to the CLI from anything that cannot import
Python in-process: a shell script, a CI job, or an agent that can run commands but not
load a Python object. Both reach the same capabilities.
