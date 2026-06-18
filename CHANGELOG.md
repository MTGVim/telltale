# Changelog

## 0.0.7

### Added
- Emoji route progress HUD guidance for `/telltale:sail`, Claude Code `/sail`, and Hermes `/sail`.
- Final convergence reports now include a `🗺️ Route Progress` section with reached island count, sailing status, current island, and last reached island.

### Fixed
- Added regression coverage so smoke reports keep the island/sailing progress markers visible.

## 0.0.6

### Fixed
- Bundled JSON schemas with the Claude Code `/sail` skill and Hermes `/sail` skill surfaces so helpers do not require or encourage `schemas/` inside user repositories.
- Added a regression test proving all helper entrypoints run from an external project without creating `<project>/schemas`.

## 0.0.5

### Added
- Doctor diagnostics via `python3 scripts/telltalectl.py doctor`.
- Example-driven first-run documentation in `docs/examples/fix-failing-test.md`.
- CI validation workflow for schema, smoke, doctor, and unit tests.
- Release checklist in `docs/release-checklist.md`.

### Changed
- Tightened README install, verification, and troubleshooting flow.
- Synchronized version references across public manifests, package metadata, README, and skill frontmatter.
- Documented internal phase alias files so guidance paths are explicit.

### Fixed
- Release/version mismatch between repository manifests and GitHub release surface.

## 0.0.4

### Fixed
- Resolved `telltalectl.py` schema lookup so `/sail` can run from external project directories while keeping state in the project workspace.
