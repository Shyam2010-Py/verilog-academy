# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
semantic versioning for its own source.

## [1.0.0] - 2026-11-25

First complete local release candidate. Not published or deployed.

### Added

- Production homepage and the Midnight/Daylight design system.
- Learning dashboard with real progress, recent activity and validated JSON
  export/import.
- 23 EC-405 theory lessons with runnable examples and completion controls.
- EC-410 laboratory landing page and six complete experiment pages.
- Interactive Circuit Lab with 18 working demonstrations, live SVG wiring,
  Boolean expressions, truth tables and a clocked D flip-flop.
- Verilog Playground with 14 verified projects, a highlighted two-file editor,
  `.v` downloads, optional local drafts and a local Icarus workflow.
- Four practice quiz banks with 46 explained questions and local attempt
  history.
- Windows and Android setup guides, plus a shared guide hub.
- 43 verified Verilog examples with recorded Icarus transcripts.
- Build, verification, preview and browser-audit tools.
- `.gitignore`, `.gitattributes`, `.editorconfig`, contribution and security
  policies, and this changelog.

### Changed

- Release labels no longer expose internal development phase numbers in the
  user interface.
- Module headers now describe current behaviour instead of development history.
- Header navigation collapses below 1080 px and uses a compact layout from
  1081-1240 px.

### Fixed

- Wordmark overlap at medium desktop widths.
- Malformed quiz storage falls back to an empty history without console errors.

### Security

- No API keys, passwords, tokens, personal paths or private credentials are
  present in the repository.
- Quiz attempts, Playground drafts and progress use separate storage keys.

### Documentation

- Added font provenance and the full SIL OFL 1.1 text with all three copyright
  notices.
- Added `GUIDE.md` and refreshed `README.md`.
- Added `docs/final-audit/REPORT.md` with the cleanup and licensing audit.

### Known limitations

- Lighthouse has not been run because no public URL exists and no local
  Lighthouse CLI is installed.
- The Android guide was verified in Chrome device emulation, not on a physical
  handset.
- The exact download URL and subsetting step for the bundled font files were
  not recorded.
