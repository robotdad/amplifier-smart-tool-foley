# Foley caller contract v1

DRAFT, unratified. Core below is proposed, not locked. H/E keys refer to
[direction provenance](../docs/direction-record.md); the
[canonical vision](../docs/00-vision.md) governs intent. IDs remain stable through draft edits.

Seam: agents and automation consuming Foley's public library, CLI, help and results.
Silent changes break their ability to request, identify and recover work. Internal
process layout and synthesis implementation are not separate contracts.

## Core

### F-C01: Discover and invoke the workflow [H1, E1]

An installed Smart Tool exposes discoverable capability help and structured results for create, inspect/list, revise, deterministic render/variants, export and audition. Every domain capability is reachable through the library; CLI operations are thin access to those capabilities. Help distinguishes model-backed from deterministic work and explains inputs, outputs and actionable failures. These are capability concepts, not frozen command spellings.

### F-C02: Choose intelligence explicitly [H3, E2]

Model-backed work uses public Amplifier Agent APIs with support for OpenAI, Anthropic, Gemini, ChatGPT and GitHub. Respect the selected provider/model and supported effort setting. Never silently substitute another provider/model. Record requested settings and observed effective settings separately; unavailable effective values remain unknown. Supported adapters, authentication readiness and live-tested operations are separate claims.

### F-C03: Refuse honestly and protect credentials [E2, E6]

Missing authentication, unavailable models, invalid requests and failed generation produce actionable errors, not successful creation receipts. Noninteractive generation does not initiate an unexpected login. Credentials do not enter sound artifacts, prompts, exported metadata or ordinary logs. Model output cannot obtain arbitrary shell execution or unvalidated synthesis-program execution.

### F-C04: Identify retained work and revisions [H1, E3]

A successful create/revise identifies a retrievable exact revision. Revision takes an explicit retained parent and preserves it, including when the new attempt fails. Supported production changes include duration and sound-character changes, not only textual relabeling. Brief, scene, seed, synthesis source, output hash and available provider/model provenance remain attributable to that revision. Partial or unknown outcomes are not reported as completed outputs.

### F-C05: Use retained work without intelligence [E1, E3]

Inspect/list, deterministic render/variants, export and audition of retained scenes work without provider credentials or model requests. Missing Csound or another actual local prerequisite is reported with a remedy, not replaced with a model call.

## Surface grid

REQUIRED means the promise must exist on that surface; IDIOM permits a different
presentation, not extra authority. EXCLUDED is deliberate for this draft.

| Capability | Public library | CLI | Static audition |
|---|---|---|---|
| Author/revise through chosen provider | REQUIRED | REQUIRED | EXCLUDED |
| Inspect, render and seeded variants | REQUIRED | REQUIRED | EXCLUDED |
| Export and produce audition handoff | REQUIRED | REQUIRED | EXCLUDED |
| Identify, play and download handed-off versions | REQUIRED (handoff data) | IDIOM (artifact reference) | REQUIRED |

No MCP, authoring dashboard or live product service is required. A new supported
surface requires reconciling this grid, not assuming parity or inventing a reduced promise.

## Backlogged

- Interactive provider-login UI: promote on an observed onboarding failure and steward acceptance of the new surface.
- MCP or live authoring UI: promote when a concrete host workflow cannot use agent/CLI plus static audition and new scope is accepted.
- Automatic retry/resume: promote on a measured ambiguous outcome and a specified identity/receipt protocol. Current honesty and retention promises remain; no blind retries are authorized.

## Conformance

Results live separately in the [clause evidence baseline](../docs/clause-evidence.md).
These are falsifiers and required checks, not declarations that all checks ran.

- F-C01: installed help advertises an unreachable workflow or wrapper-only behavior.
  Check installed help/manifest, library/CLI traces outside checkout, valid and
  invalid invocations, structured results and errors.
- F-C02: provider A silently becomes B, or a five-provider claim rests on one success.
  Keep a per-provider adapter/auth/live matrix and requested/observed settings.
  Exercise public Agent integration and a live creation on each ready provider;
  retain access blockers. One-provider creation is not five-provider revision parity.
- F-C03: missing auth reports success, launches login, leaks a canary or executes
  hostile output. Use isolated missing-auth/bad-model/hostile-output fixtures and a
  valid control, inspect retained artifacts, use synthetic canaries, not real secrets.
- F-C04: duration revision fails, modifies its parent, loses a usable version or
  only changes metadata. Check exact parent IDs, before/after hashes, decoded audio,
  a failed-revision fixture and retrieval/export of both versions.
- F-C05: deterministic work asks for keys or calls a model. Exercise the full
  deterministic workflow with credentials absent and outbound network denied;
  include a missing-local-runtime negative case.

Current verification baseline: Agent binding AND engine 0.22.0. Record installed
versions. This is a revisable engineering baseline, not a permanent product pin.
Campaign scope and budgets remain with the parent; this draft adds no calls.

## Reserved

No extra command names, schema fields or provider aliases are reserved. Internal
runtime classes, storage layout and compiler structure are not public API promises.

## Changelog

No accepted changes. Draft integrated prospectively; entire document remains unratified.
