# Foley

Status: DRAFT, unratified implementation direction, derived from the owner's request.
This remains the single canonical vision. The proposed contracts are not locked.

## Source intent

Marc Goodner requested in the originating conversation:

> Let's make a smart tool for making sound effects, use csound for the engine. Setup a new repo on my user for this it can be public. I want users to be able to work with their agent and describe what they need in terms of sounds. The aim is effects for use in media productions, video games, etc. The aim is not music making but I wouldn't wall it off, but the point is sound effects, like a foley artist. Take this as complete as you can without further input from me. Keys needed for the services should be in place. The choice for the intelligence in this should be amplifier agent, support openai, anthropic, gemini, chatgpt, and github as providers. Use the dtu smart tool for validating how well it works. Only bother me if you are blocked or you have an end to end experience I can try.

## Product interpretation

Foley is an agent's sound-effects workshop. A person describes an effect, its timing, material, action and production context. The tool uses Amplifier Agent to design a structured sound scene and Csound to synthesize the actual audio. The caller can audition, request changes against an exact retained version, make seeded variations, and export usable assets. This is procedural sound design, not a promise of indistinguishable recorded real-world foley.

## Operating principles

1. Sound effects come first. Pitched and musical sounds remain possible.
2. Deliver sound, not just instructions for making sound.
3. Make creative iteration safe: keep the original and make the chosen version clear.
4. Judge usefulness against the brief, not an unattainable standard of recorded realism.
5. Let people work through their agent without learning synthesis programming.
6. Keep provider choice explicit and claims proportional to observed evidence.

Proposed external promises live in [caller](../contracts/caller.v1.md),
[media](../contracts/media.v1.md) and [audition](../contracts/audition.v1.md).
[Direction provenance](direction-record.md) preserves the later product requests,
human requirements and revisable engineering interpretations.
[Clause evidence](clause-evidence.md) separates implemented behavior, observed
checks and not-yet-verified promises. These records adopt Converge practices
prospectively; they do not retroactively establish Converge-compliant execution.

## Goals and acceptance

- Natural-language creation and revision produce real playable sound, not merely a prompt, patch or code sample. Test physical/material effects, designed game effects and ambience.
- Csound is the synthesis engine. A deterministic typed scene and trusted compiler allow layered, timed synthesis without running arbitrary model-authored programs or shell commands.
- Preserve the original brief, scene, seed, synthesis source, audio hash, provider/model provenance and immutable parent revision. A failed attempt cannot erase a usable original.
- Support OpenAI, Anthropic, Gemini, ChatGPT and GitHub through public Amplifier Agent APIs. Provider choice is explicit and never silently substituted. Distinguish implemented support from live verified access. Missing auth has actionable errors; noninteractive generation does not unexpectedly launch login.
- Agent-friendly library and thin CLI with full capability help, structured results, a Smart Tool manifest/descriptor and installable package. Deterministic render, inspect, export and audition need no model credentials.
- Production-ready WAV exports at 48 kHz / 24-bit by default, mono/stereo choices, controllable duration, seeded variants and a loop option. Validate actual audio duration, finite non-silent samples, headroom and loop treatment. Be honest about what a loop check proves.
- A self-contained audition experience exposes actual generated audio and associated descriptions and versions. The user can listen and download without understanding Csound. Prefer a small complete experience over a large unfinished dashboard.
- Verify an installed distribution using the DTU smart tool, retaining commands, outputs, hashes, failures and provider evidence. Mechanical sound checks do not prove perceptual realism. Preserve the sounds for human review instead of claiming unheard audio was judged.

## Boundaries

- Sound effects are the primary workflow; pitched or musical sounds are not prohibited.
- This is not a DAW, sample marketplace, voice cloning system, recording studio or video editor. External recordings and arbitrary Csound code are not required for the initial release.
- Resource bounds protect rendering and storage; do not recreate unsupported Agent internals to enforce invented model-call or token budgets.
- User credentials remain outside repositories, artifacts and logs. Model output is untrusted. No inherited coding/shell tools are needed for sound design.
- Cross-platform instructions may be supplied, but platform verification is reported only for environments actually exercised.
- A hosted service, large authoring dashboard or MCP surface is not required to
  make and audition an effect. API success and silent WAVs are not sound delivery;
  playback success is not listening-based evaluation.

## Working decisions

- Product name and command: Foley / `foley`.
- Public source: https://github.com/robotdad/amplifier-smart-tool-foley.
- Initial delivery emphasizes create -> audition -> revise -> compare -> export, plus deterministic recipes for discovering and testing the engine. These engineering choices are revisable within the source intent.

## Accepted contract changes

None. Integration of these drafts is not their ratification or a freeze decision.
