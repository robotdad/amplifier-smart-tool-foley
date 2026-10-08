# Foley media contract v1

DRAFT, unratified. Core below is proposed, not locked. H/E keys refer to
[direction provenance](../docs/direction-record.md); see the
[canonical vision](../docs/00-vision.md).

Seam: production editors, game developers and downstream asset tools depend on
actual audio, version identity and exports. Compiler algorithms and database
structures are internal mechanisms, not additional contracts.

## Core

### F-M01: Synthesize real sound with Csound [H1, H2, E6]

Successful sound creation includes actual Csound-synthesized, decodable audio. A scene, patch or provider response alone is not a sound deliverable. Validate model-authored design data before synthesis. Unsupported or invalid data fails explicitly rather than executing arbitrary generated code.

### F-M02: Deliver usable sound matching the brief [H1, E4]

Audio reflects the requested action, temporal pattern and material or designed character well enough for the stated production purpose. Procedural stylization is acceptable; perfect realism and aesthetic perfection are not required. Music is not prohibited globally. A particular brief's exclusions, such as no voice or music, do apply to its output. Metadata cannot stand in for the sound itself.

### F-M03: Preserve production format and signal integrity [E4]

Default production export is WAV at 48 kHz, PCM 24-bit, with requested mono/stereo and duration. Within supported ranges, actual decoded frame count matches requested duration rounded to one frame; unsupported requests are rejected explicitly. Successful non-silent effect requests produce finite, nonzero audio with peak below digital full scale and no clipping runs. No universal loudness target is imposed. Preview derivatives do not replace the production master.

### F-M04: Retain and export the exact chosen revision [E3]

Original and revised brief, scene, seed, synthesis source and audio are immutable retained artifacts. Export identifies its exact source revision and matches that revision's production audio. If a documented export conversion changes bytes, retain source identity and verify its stated transformation; never label a preview derivative as the master. Failed generation or export does not corrupt an existing usable revision.

### F-M05: Repeat a seed and distinguish variants [E3, E4]

The same retained scene and seed reproduce decoded PCM in the same pinned synthesis environment. Different seeds of a noise-bearing scene produce distinct audio while preserving declared structure, timing and format. Different IDs or WAV metadata alone do not count as variants. No cross-platform bit-identical claim is made.

### F-M06: Treat requested loops as loops [E4]

A requested continuous loop preserves continuity at repeated joins without conspicuous clicks, pauses or repeated fade dips. Output includes actual loop treatment, not only a loop label. This is a bounded functional promise for requested loop material, not a universal perceptual certification for every playback system.

## Backlogged

- Compressed production formats or engine-specific packages: promote on a downstream import failure that WAV cannot meet, with scope accepted.
- External samples or caller-supplied Csound programs: promote on a demonstrated sound-design need and an accepted input/trust contract.
- Cross-platform bit-exact reproduction: promote only with a downstream requirement and supporting multi-platform evidence.

## Conformance

The [clause evidence baseline](../docs/clause-evidence.md) separates mechanical and
perceptual observations. These requirements are not completed-test claims.

- F-M01: success returns only code, silence or non-Csound audio. Retain actual
  Csound invocation/version, scene/CSD and output; fully decode audio; discriminate
  valid design from malformed/hostile rejected design.
- F-M02: four requested steps become steady buzz or a metallic hit has no attack/ring.
  Check physical, game/interface and ambience briefs against raw audio, event/envelope
  measurements and qualified independent audio-content review with obvious good/bad
  controls. Preserve exact briefs and input hashes.
- F-M03: wrong channels/duration, mislabeled float/16-bit master, nonfinite samples
  or clipping. Fully decode and measure format, frames, peak, clipping and energy;
  use wrong-format/truncated/clipped controls.
- F-M04: exporting B yields A, original hashes change or failure erases usable audio.
  Compare before/after manifests, decoded PCM and exports; inject failure and retrieve
  both versions afterward.
- F-M05: same-seed PCM differs or noise variants are identical. Render the same
  numeric scene twice with the same seed and with three distinct seeds; compare
  decoded PCM hashes/difference energy and scene structure. Include a metadata-only
  fake-variant negative control. Recipe parameter jitter alone does not prove this.
- F-M06: a labeled loop clicks or drops to silence on repeat. Check three concatenated
  cycles for boundary jump/slope and local RMS/spectrum against interior transitions;
  independently review joins using smooth, discontinuous and fade-dip controls.

Retain actual thresholds and raw measurements. Event names, spectrograms and playback
are not proof of perceived character. Without a qualified audio reviewer, F-M02 and
perceptual F-M06 stay unverified while mechanical work continues. Judgment facets
must remain attributed, never manufactured machine passes. No new calibration
campaign or provider calls are authorized by this draft.

## Reserved

No file extensions beyond the proposed WAV master are reserved. Scene/CSD retention
provides provenance and rerender inputs within declared compatibility, not a stable
cross-version import format or permission to execute arbitrary Csound.

## Changelog

No accepted changes. Draft integrated prospectively; entire document remains unratified.
