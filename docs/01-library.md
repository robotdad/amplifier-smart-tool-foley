# Library direction

Every capability is reachable from `foley.lib`; CLI and optional MCP adapters only parse and project library calls. The implementation will fill in exact signatures and help alongside the code.

## Core workflow

- `create`: natural-language brief plus explicit provider/model, duration, channels, seed and loop preference -> immutable rendered revision and provenance.
- `revise`: exact prior revision plus change request, explicit provider/model and optional changed duration -> new rendered child revision, original untouched.
- `render`: validated typed sound scene -> rendered immutable revision without intelligence.
- `variants`: exact revision and explicit seeds -> independently retained deterministic alternatives, preserving the base.
- `list` / `inspect`: discover retained sounds, exact metadata, scene and validation evidence.
- `export`: exact revision -> WAV and optional portable bundle containing scene/CSD/provenance. Export paths are caller-owned, never model-authored.
- `audition`: exact retained revision(s) -> self-contained HTML listening/comparison surface with embedded audio and downloads. It must not require an external CDN or rerun generation.
- `doctor`: deterministic installation, Csound and provider configuration readiness, without exposing credentials or making a paid call.
- `manifest`: deterministic Smart Tool manifest.

## Domain model

A sound scene contains bounded duration, sample rate, channel count, seed, loop mode and typed layers. Layers specify timing, envelope, gain, source type, pitch/filter motion and pan, permitting original combinations instead of a closed preset selector. A trusted compiler turns validated numeric/enumerated data into Csound. Text is metadata, never inserted as executable code. Render in a private temporary directory with fixed output path, bounded process lifetime and no caller-controlled flags.

Store each published revision atomically in its own directory. Identify parent revisions explicitly; reject traversal and missing targets. Publish only after successful audio validation. Keep failure diagnostics separate from successful result state. Never represent a missing, silent or malformed render as success.

Compiler version 2 gives each noise layer an explicit deterministic `rand` seed
strictly between 0 and 1 and selects its 31-bit generator. The global Csound seed
does not control this opcode. Changing only a scene seed now changes actual noise;
old compiler-version-1 artifacts are preserved, not regenerated or rewritten.
Reproducibility means the same scene, seed and compiler/engine environment, not
byte identity across this compiler correction.

The renderer subprocess inherits only PATH, SystemRoot/SYSTEMROOT, WINDIR,
COMSPEC, PATHEXT, LD_LIBRARY_PATH, DYLD_LIBRARY_PATH,
DYLD_FALLBACK_LIBRARY_PATH, OPCODE6DIR and OPCODE6DIR64. These are trusted
operator executable, DLL/library and Csound plugin paths, not scene inputs.
HOME, USERPROFILE, XDG_CONFIG_HOME, TMPDIR, TMP and TEMP point to its private
temporary directory; LC_ALL is C. No provider credentials, proxy settings,
Agent settings or other ambient variables are forwarded. FOLEY_CSOUND is resolved
by the parent into the fixed executable path, not passed as a renderer variable.
This narrows inheritance; it is not a sandbox against a malicious installed engine
or a hostile same-user process.

## Intelligence

The sole shipped intelligence runtime is Amplifier Agent behind the `Intelligence` protocol. Use public session/turn APIs and structured submission. Provider identifiers map openly to OpenAI, Anthropic, Gemini, ChatGPT and GitHub Copilot; no direct service SDK fallback. Supply only sound-design tools/schema and the actual prior scene during revision, not filesystem or shell tools. Preserve caller model and supported effort configuration. Lazy imports keep deterministic work provider-free.

The original Creator scaffold's Copilot SDK implementation was replaced with
Amplifier Agent; there is no second intelligence path.

## Verification

Offline tests cover admission/scene validation, malicious strings, path constraints, atomic lineage, retained originals, failed renders, provider configuration, CLI help and packaging. Real Csound tests prove sound rendering and audio properties. DTU installed-product trials prove create/revise/export across representative requests and available provider access. Document unsupported or untested paths rather than substituting mock evidence.

## Implemented entry points

```python
from pathlib import Path
from foley import lib

scene = lib.recipe("wood-impact", duration=2, seed=17, channels=2, loop=False)
original = lib.render(scene, store=Path("./sounds"), brief="Wooden prop impact")
lib.audition([original["id"]], Path("listen.html"), store=Path("./sounds"))
lib.export(original["id"], Path("wood.wav"), store=Path("./sounds"))
```

`create(brief, store=None, provider="openai", model=None,
duration=2, channels=2, seed=1, loop=False, reasoning_effort="medium", timeout=300)`
returns a revision dictionary. `revise(revision, changes, ..., duration=None)`
inherits duration unless changed and preserves channels/seed/loop. Both accept an
optional `intelligence` implementation for controlled testing. Model defaults live
in schemas.py's DEFAULT_MODELS map; omitted models select the chosen provider's
default. An explicitly supplied model is never substituted.

`variants(revision, seeds, store=None)` returns up to eight child dictionaries.
`inspect(revision, store=None)` verifies payload hashes and returns metadata.
`list_sounds(store=None)` lists retained revisions. `export(revision, destination,
bundle=False, store=None)` writes a new WAV/ZIP. `audition(revisions, destination,
store=None)` writes self-contained HTML. `doctor(providers=False)` checks readiness.
`models(provider)` uses public Agent discovery; catalogs can require network access.

`Scene` and `Layer` in `foley.scene` expose the complete JSON schema, bounds and
temporal validators. Deterministic paths do not import `amplifier_agent`.
Existing export/audition destinations are refused. A variants batch retains any
already-published children if a later render fails. Integrity hashes detect
accidental changes, not a hostile same-user writer replacing data and hashes.
