---
name: foley
description: >-
  Design, audition, revise, and export production sound effects with Csound and Amplifier Agent. Drive it from the command line as `foley`, or from Python through
  `foley.lib`. Triggers on "foley".
license: MIT
metadata:
  repository: https://github.com/robotdad/amplifier-smart-tool-foley
---

# Using foley

Design, audition, revise, and export production sound effects with Csound and Amplifier Agent.

## Install

```bash
# as a CLI
uv tool install git+https://github.com/robotdad/amplifier-smart-tool-foley

# as a library, from another project
uv add "foley @ git+https://github.com/robotdad/amplifier-smart-tool-foley"

# once, without installing
uvx --from git+https://github.com/robotdad/amplifier-smart-tool-foley foley --help
```
## Use it

Run `foley --help`. It prints the tool's skill: when to use it, every capability, sharp
edges, and which files to read. Follow it. Then read the capability's own skill with
`foley <command> --help` before calling it: it carries the arguments, a worked
invocation, the result, and the failures. Never work from memory.
