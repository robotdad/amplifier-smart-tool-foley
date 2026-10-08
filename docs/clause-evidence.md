# Draft-clause evidence baseline

Single baseline for the DRAFT contracts [caller](../contracts/caller.v1.md),
[media](../contracts/media.v1.md) and [audition](../contracts/audition.v1.md).
See [canonical vision](00-vision.md) and [source authority](direction-record.md).
This is an assessment worksheet, not a seeded Converge ledger, executable contract
kit, ratification or product-completion claim. Implementation and observation differ.

## Candidate and evidence identity

### Final initial-build qualification

This summary supersedes the historical pending entries below without rewriting
their evidence. Final wheel SHA256:
`deb6800ce5fee902c68da193d4ad4b7a79375dfbbbe0249253dbe4d44fe9d7ff`.
Parent independently verified 131 source tests and all 52 source/wheel package
files; DTU qualification passed 130 installed tests and 16 conformance checks
with Agent binding and engine 0.22.0. All 13 retained revisions were copied and
hash-verified before the owned DTU was destroyed.

Live outputs were retained through OpenAI, Anthropic, Gemini and GitHub Copilot.
ChatGPT live access remains unverified because OAuth login was missing.
Independent browser checks passed 350 assertions across five exported pages and
ten cards, including exact downloads, loop playback and offline reopening.
These are delivery checks, not listening judgments.

F-C04/F-M02: the final changed-guidance metal-impact revision still did not reduce
measured post-impact ringing. Its 100-500 ms tail energy changed by +0.011 dB.
F-M06: the ventilation loop has a repeated 20.6 dB dip over the 20 ms join window
despite equal endpoints. The continuous-loop goal is unmet, not merely untested.
No qualified perceptual review is available. The full reports remain in workspace
`.work/foley-final-live/`, `.work/foley-jules-audio-check/`,
`.work/foley-final-browser/` and `.work/foley-handoff/FINAL-STATUS.txt`.
Publication does not ratify these drafts or erase either unmet result.

Prior candidate: wheel SHA256
`b44cd0ce85aa599cbf652d3f5f4ec3788878c363efe63e0ecb13017b32a91b3a`,
source freeze `2878ac0c651b334bf1e32649d4e58bf123a9c010dff1a2155ea56c5b20cc70e1`.
Builder observed 118 source tests, 117 installed tests and 16 conformance checks
passing. Parent separately reports verification of 72 source hashes, 52 package
files and DTU installed 117 tests / 16 checks with Creator 0.3.1. These are historical
results, not evidence that the corrected candidate passed every acceptance promise.

Correction1 changes compiler seeding/environment and integrates these drafts. Its
local `freeze.json` records per-file hashes, exact wheel, installed equality and
runtime versions. Source tests are reproducible from this repository; copied tests
must import the installed wheel outside the checkout. Detailed local files named
below are evidence references, not shipped hyperlinks:

- Repository `.work/final-evidence/` preserves prior candidate reports and wheel.
- Repository `.work/correction1/` holds fail-first, corrected checks, package and freeze evidence.
- Workspace `.work/foley-independent-review/REPORT.txt` and
  `.work/foley-acceptance/parent-review.txt` preserve independent and parent findings.

During qualification the implementation was uncommitted, so the recorded source
and wheel hashes, rather than the scaffold's HEAD, identify each tested candidate.
Actual runtime baseline is Linux arm64, Python 3.13, Csound 6.18 and Agent binding
AND engine 0.22.0. No cross-platform or perceptual acceptance is asserted here.
Builder synthetic loopback provider tests are not live inference; parent-attributed
live evidence below concerns the old candidate, not correction2.

Correction1 observed check summary: 125 source tests and 124 copied installed-wheel
tests pass, zero skips. Ruff, formatting, ty, prek, build and diff checks pass.
Creator 0.3.1, invoked from its upstream main without updating the global install,
reports 16 pass / 0 fail / 0 skip against the extracted source distribution. Creator
uses that extracted project's uv environment; the separately installed-wheel tests
are distinct evidence. Those tests also pass with the parent's non-sudo extracted
Csound wrapper. No DTU installation or paid/provider generation was changed here.
Seven fail-first cases and their corrected passes are retained separately.

Correction2 addresses the completed independent browser review's one defect:
144/146 checks passed, but loop=true Wind stopped at 2 seconds on both desktop and
narrow viewports. The report was read directly from workspace
`.work/foley-browser-validation/REPORT.txt`; it exercised the byte-identical relocated
old deterministic sampler in Chromium 153 at 1280x900 and 390x844. Passing evidence
included native play/pause/seek/end, fifteen exact-WAV downloads with full decode,
metadata, responsive controls and fresh-context offline reopen. This is not a full
pass and not an audio-content judgment. Correction2 propagates retained scene.loop
to the native player, visibly labels Loop/One-shot and adds a fail-first mixed-card
regression. Its new sampler reuses existing audio; prior sampler/evidence stays intact.
Actual corrected-export boundary wrapping remains for parent browser qualification.

Parent reports that live Alex testing on OLD installed wheel b44cd0ce completed an
OpenAI 2-second creation and a 1-second revision, with parent-verified hashes and
full decode. This is attributed completion evidence, not independently rerun by this
builder. Its exact two-card export is being checked separately; it is not modified
or substituted here. No perceptual matching, other-provider outcome, correction2
live outcome or documentation ratification follows from that report.

Correction3 qualification corrects any implication that Alex's requested reduction
of ringing was met. The independent report and `root-cause-evidence.json` in workspace
`.work/foley-alex-audio-check/` were read directly. Original
`76d9801213ca4b01a9e16b9831f966dd` and child `fdc35fb6462b41ec975f52f7e499eb29`
remain a workflow, format and duration-change pass, but **less-ring acceptance is
unmet**: the measured post-impact AC tail is unchanged to PCM24 precision.
All six edited ring layers had sustain=0; the long release was a silent 0-to-0
segment. Their original positive envelopes ended by 46 ms. An unchanged body layer
explains the surviving oscillating tail. The author changed relevant parameters;
the model-facing schema lacked their exact envelope meaning. No listening verdict
or provider-wide failure rate follows from this one pair.

Correction3 adds truthful Layer field descriptions and authoring instructions:
duration includes the three linear stages, the middle is a ramp rather than a hold,
sustain is the level at release start, and zero sustain makes release silent.
Zero remains valid. Compiler semantics, schema bounds/defaults, retry behavior and
all original audio stay unchanged; no special case for this example is introduced.
Deterministic PCM fixtures distinguish zero/positive sustain and short/long release
using per-window AC energy to avoid mistaking constant DC padding for a tail.
Public-Agent loopback checks verify the descriptions and instructions actually
reach the submission request. These checks prove explanation/implementation
agreement, not improved live authoring quality. Parent owns a separately authorized
live check; this correction does not upgrade the DTU or interrupt its current trial.

## Observations by clause

Each row keeps implementation, observed checks and not-yet evidence distinct.
The parent owns remaining independent qualification; this record grants no new calls.

### F-C01

Implemented: library workflow, thin CLI, packaged full capability skills and manifest.
Observed: `test_skill.py` verifies the command/skill inventory and every argument;
installed copied tests and conformance exercise discovery. `installed_smoke.py`
exercises actual rendering, variants, inspect/list, audition and export.
Parent-attributed: old-wheel OpenAI create/revise completed as recorded above.
Not yet: complete corrected-candidate workflow and exact live-export browser acceptance.

### F-C02

Implemented: five canonical provider routes, aliases, centralized defaults, explicit
model preservation, requested/configured and observed event settings in provenance.
Observed: `test_explicit_selection_honored` and `test_provider_default_models` use
labeled test doubles; `test_public_agent_against_local_endpoint` uses real public
Agent/engine with a synthetic HTTP endpoint. Prior public discovery finds all five
installed, four credential-ready and ChatGPT missing login; availability is not entitlement.
Parent-attributed: old-wheel OpenAI creation/revision succeeded. Not yet: actual
generation/revision per other provider and qualified corrected-candidate access matrix.
No blanket five-provider success claim.

### F-C03

Implemented: typed submission only, sole caller tool, no shell/MCP/skills, isolated
Agent config, renderer path allowlist and private home/temp environment.
Observed: compiler hostile-string/range tests, public invalid-submit recovery,
no-submission and failed-terminal tests, secret marker absent from returned results.
Correction canary test checks the actual renderer invocation has no synthetic provider,
unknown-secret or proxy variable and still renders with the extracted engine.
Not yet: all real-service absent-auth/bad-model cases. No exploit/exfiltration claimed.

### F-C04

Implemented: immutable retained revision and parent, changed-duration child, brief,
change request, seed, CSD/audio and provider provenance.
Observed: `test_complete_create_revise_compare_export` changes duration 1s to 3s
using controlled Intelligence and real Csound; parent hashes remain intact.
`test_failure_leaves_original_and_no_partial_revision` checks failed rendering.
Parent-attributed: old-wheel live OpenAI duration change 2s to 1s succeeded with
hash/decode verification; no new live trial was performed by this correction.
Counterevidence: Alex's less-ring request is unmet despite successful duration
change; see correction3 above. Not yet: corrected-guidance live semantic revision proof.

### F-C05

Implemented: lazy Agent imports and deterministic retained-work path.
Observed: `test_deterministic_import_never_loads_agent`, provider-scrubbed conformance
help/manifest and installed deterministic smoke. Renderer canaries are not forwarded.
Not yet: the complete deterministic matrix under external network denial and a
missing-local-runtime fixture. Lazy imports alone do not prove that broader matrix.

### F-M01

Implemented: bounded scene, trusted numeric compiler, actual Csound process and
validation before publication.
Observed: real nine-recipe mono/stereo rendering, impulse, fixed-command timeout,
malformed/silent/nonfinite rejection and compiler injection tests.
Parent-attributed: old-wheel OpenAI creation/revision produced decodable audio.
Not yet: parent correction-wheel DTU/provider recheck and semantic sound acceptance.

### F-M02

Implemented: composable layered design surface and recipes; this is a mechanism,
not proof of matching material, action count, texture or exclusions.
Observed: no qualified audio-content verdict. Parent reports Gemini qualification
controls failed; those judgments cannot be reused as acceptance.
Measured counterevidence: the Alex pair's active tail did not get shorter or quieter;
changing metadata and file duration cannot discharge its less-ring request.
Not yet: raw actual creations checked against briefs by a qualified audio reviewer,
with discriminating good/bad controls. Authored names and waveform tests are insufficient.

### F-M03

Implemented: 48 kHz PCM24, mono/stereo, exact rounded frames, finite/non-silent check,
DC removal and peak attenuation to -1 dBFS without boosting quiet synthesis.
Observed: `test_real_recipes` checks 18 combinations; loop nonintegral duration,
wrong rate/channels/length, missing/malformed/NaN/silent negative cases. Independent
prior review reports a 32-layer clipping stress with safe final headroom.
Not yet: repeat the independent stress on the corrected wheel; no claim that every
possible scene meets artistic loudness expectations.

### F-M04

Implemented: exact revision exports, retained originals, fixed-member deterministic ZIP.
Observed: before/after parent payload comparison, same-revision ZIP byte equality,
WAV hash equality and tamper/symlink refusal in `test_workflow.py`. Correction rain
variants test compares every original file before/after new children.
Not yet: actual-browser chosen-version download evidence for the corrected candidate.

### F-M05

Implemented correction: explicit deterministic per-layer rand seed in (0,1), 31-bit
selector, compiler_version 2. Prior artifacts remain compiler-version-1 artifacts;
reproduction is within the same compiler/engine, not across a compiler correction.
Observed failure first: all seven new focused cases fail on prior compiler/environment,
including pure-noise PCM identity and public rain variants. Corrected focused cases
pass: identical numeric scene/seed reproduces PCM; changing only seed changes PCM
for seeds 1, 2, 17 and 2147483646 in mono/stereo; public rain variants differ while
same-seed repeated child reproduces and parent files remain unchanged.
Not yet: independent parent rerun and corrected-wheel DTU reproduction. Recipe
parameter jitter alone is explicitly not accepted as the seed proof.

### F-M06

Implemented: symmetric boundary smoothing at unchanged frame count.
Observed: `test_loop_length_and_boundary` proves rounded duration and zero endpoint
delta, not continuous perceived ambience or absence of repeated envelope dips.
Not yet: three-cycle local energy/slope/spectrum checks and qualified listening at
joins with discontinuity/fade-dip controls. The stronger draft promise remains open;
this correction does not modify loop treatment to manufacture a pass.

### F-A01

Implemented: immutable-ID cards with embedded actual WAV, descriptions, parent and seed.
Observed: tests check two embedded audio players, exact IDs and escaped hostile markup.
Observed in prior browser report: all five card identities, embedded media, descriptions,
parents, seeds and downloaded bytes matched retained records. Not yet: corrected-export
browser recheck and deliberate label/media negative controls. No selection UI is required.

### F-A02

Implemented: native audio controls, responsive cards and correction2 native loop
attribute only for retained loop scenes, with visible Loop/One-shot labels.
Observed in prior browser report: desktop/narrow native gestures work and all four
one-shot cards end; Wind incorrectly ends too (two failures of the same defect).
Correction2 regression fails before the fix, then checks mixed-card attributes,
labels, no autoplay, unchanged exact media/download bytes and no regeneration.
Not yet: actual corrected-export native wrapping plus one-shot end in the browser,
and unsupported-media behavior. HTML regression is not browser playback proof.

### F-A03

Implemented: each card downloads its embedded production WAV with an exact-ID name.
Observed: library exports match retained audio and HTML embeds WAV bytes.
Observed in prior browser report: fifteen real downloads match exact retained masters
and decoded PCM. Not yet: corrected-export and live two-card export browser rechecks.
HTML construction tests alone are not evidence of a completed browser download.

### F-A04

Implemented: self-contained HTML/data WAV with no CDN, scripts or Foley backend.
Observed in prior browser report: relocated fresh-context offline artifact preserved
all cards and exact downloads without library/backend access or external requests.
No claim of OS-wide network capture. Not yet: corrected-export recheck and cross-host
delivery. Simulated reactions must be labeled and cannot imply anyone heard the sound.

## Reproduction and assessment method

Use the source test suite with a real Csound executable, then build and install a
wheel separately. Copy tests outside the checkout; omit only source-layout-specific
manifest tests and replace them with package/descriptor conformance. Check actual
binding and engine versions, all package-file bytes and wheel dependency metadata.
Run current Creator `check-conformance` on the extracted source distribution with
its required dependencies and executable surface identified. Archive commands, exits,
raw output, source/wheel hashes and observed test skips; a skip is not a pass.

Seven correction-specific tests form the bounded fail-first subset in
`tests/test_scene_audio.py`: pure-noise PCM seeds (two channel cases), per-layer seed
bounds/31-bit selector (three edge cases), public rain variants and environment canary.
The old constant-noise behavior is the negative control; output IDs/WAV container
changes alone cannot satisfy the PCM comparison. The environment canary check runs
real Csound after inspecting the supplied child environment; it asserts absence,
not a fabricated security exploit.

For later live cases preserve physical/material, designed game/interface and ambience
briefs, exact operation/revision IDs, original audio, changed-duration revision,
selected export and loop repetitions. Provider support, credential readiness, actual
live outcomes and qualified content review are separate columns, never inferred from
one another. Use simulated-user tasks as bounded real journeys, separating observations,
simulated reactions and hypotheses. A failed evaluator qualification blocks judgment
claims, not unrelated deterministic verification. Preserve campaign budgets and let
the parent own further admissions.
