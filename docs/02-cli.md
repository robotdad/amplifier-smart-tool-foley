# CLI Reference

The CLI is a thin wrapper over the [library](01-library.md): one command per capability, taking the same arguments under the same names, and doing nothing the library does not. 
What each argument means and what a capability returns or raises is documented there. This page covers only what the CLI adds: the invocation shape, and what reaches stdout, stderr, and the exit code.

Results go to stdout and diagnostics to stderr. A failure the library can name prints its message to stderr and exits 1; a bad invocation exits 2.

## Help

```
foley -h                 terse summary for a person: the commands, a line each
foley --help             the tool's skill, written for an agent driving it
foley <command> -h       terse summary of one command: its arguments and defaults
foley <command> --help   that command's skill, written for an agent about to call it
```

`--help` on the tool prints what `lib.skill()` returns and on a command what `lib.skill("<command>")` returns; the CLI adds nothing of its own.

## foley manifest

```bash
foley manifest
```

`lib.load_manifest()`, printed as JSON.

## Workshop commands

```bash
foley doctor --providers
foley models --provider openai
foley create "Wooden impact" --provider openai --model gpt-6-astra --duration 2 --store ./sounds
foley revise REVISION "Softer attack" --duration 3 --store ./sounds
foley recipe --name rain --duration 4 --loop > rain.json
foley render rain.json --store ./sounds
foley variants REVISION --seed 4 --seed 5 --store ./sounds
foley list --store ./sounds
foley inspect REVISION --store ./sounds
foley audition ORIGINAL CHILD --destination compare.html --store ./sounds
foley export REVISION effect.wav --store ./sounds
foley export REVISION effect.zip --bundle --store ./sounds
```

All results are JSON on stdout. `recipe` prints only scene JSON for redirection.
`--help` carries every parameter and failure; `-h` shows parser defaults.
Capability names map to library functions except `list` -> `list_sounds` and
`manifest` -> `load_manifest`. No CLI-only synthesis logic.
