# Changelog

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
