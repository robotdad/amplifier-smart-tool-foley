# Foley audition contract v1

DRAFT, unratified. Core below is proposed, not locked. H/E keys refer to
[direction provenance](../docs/direction-record.md); see the
[canonical vision](../docs/00-vision.md).

Seam: people receiving an audition artifact depend on identifying, playing and
downloading the intended sound without the originating agent or Csound expertise.
Static HTML with embedded/packaged media is sufficient. No live service, authoring
dashboard or MCP application is required.

## Core

### F-A01: Identify and compare the handed-off sounds [H1, E3, E5]

The audition artifact presents the actual sounds and their descriptions with distinguishable exact revision identities. An original and its revision can both be handed off, selected and compared without overwriting either. Selection, displayed identity, player media and download target agree. There is no obligation to synthesize or revise inside the audition page.

### F-A02: Use real playback and controls [E5]

People can play, pause, seek and reach the end of a selected sound in a supported browser, using the artifact at desktop and narrow widths without losing essential controls. Requested loop material can be auditioned across repeated joins. Ordinary browser interaction to start playback is acceptable; autoplay is not required. Unsupported decoding or missing media is actionable failure, not a working-looking empty player.

### F-A03: Download the selected production asset [E4, E5]

Download yields the exact selected revision's production WAV, not another version or an unlabeled preview derivative. A derivative used for browser playback is identified and attributable to its master. Human-readable naming helps distinguish versions but is not the integrity proof.

### F-A04: Reopen and share without the author's environment [E5]

The self-contained artifact and included media remain usable when relocated away from the source library and reopened in a fresh browser session. Playback and download do not require model credentials, external network access, the original absolute paths or a running Foley/DTU process. A generic local static server is acceptable if required by a documented browser restriction; it must not require Foley-specific backend state. Returning to the handoff preserves access to the included original and revision, not a mutable latest-version lookup.

## Backlogged

- In-browser authoring, comments or collaboration: promote on a review workflow that static comparison plus agent revision cannot meet, with scope accepted.
- Hosted sharing/authentication: promote when a recipient cannot use portable handoff and additional hosting/security obligations are accepted.
- Universal browser/device compatibility: add specific targets only for an observed delivery need and testable target. Never generalize from one browser.

## Conformance

Observed results and gaps live in the [clause evidence baseline](../docs/clause-evidence.md).

- F-A01: B is displayed but A plays/downloads, or revision removes the original.
  Observe original/revised selection, DOM/media state and source hashes; include
  a label/media-swap negative control.
- F-A02: play does nothing, seek targets the wrong clip, repeat is unavailable or
  narrow controls cannot be reached. Exercise actual desktop/narrow browser controls,
  loaded state, time progression, pause/seek/end/repeat and missing/bad-media cases.
- F-A03: download is another revision, corrupt or only a preview. Perform actual
  browser downloads and independently decode/hash against the selected master;
  include wrong-target/altered-file controls.
- F-A04: reopened artifact needs original paths, process or keys. Relocate it to a
  fresh browser context with network denied and originating service absent; test
  return access to both original/new versions and an absolute-path negative control.

Record browser/platform/viewports and topology. Local relocation is not cross-host
validation. Adapt simulated-user tasks to actual public discovery and controls,
without ideal command coaching. Separate OBSERVED behavior, SIMULATED reactions and
INFERRED hypotheses. Neither a text-only persona nor a playback event hears audio.
Audio-content acceptance belongs to F-M02/F-M06. This draft authorizes no new trial.

## Reserved

No HTTP endpoints, host callbacks, collaboration roles or persistent server sessions
are reserved. A handoff is not authority to run new model work.

## Changelog

No accepted changes. Draft integrated prospectively; entire document remains unratified.
