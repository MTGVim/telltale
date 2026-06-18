# Changelog

## 0.0.9

### Changed
- `출항`, `출항이다`, `이 작업 출항하자` 자연어 요청이 `/sail` 항해 의도로 더 잘 매칭되도록 skill/command frontmatter와 진입 표면에 명시했다.
- M1은 병렬 후보를 지도에 표시할 수 있지만 기본 실행은 한 번에 하나의 현재 작업 섬만 수행한다는 안전 원칙을 문서화했다.
- 매핑 완료, 출항, 섬 완료, 전체 완료 시 상태라인과 짧은 브리핑을 제공하는 출력 계약을 추가했다.
- HUD 라벨의 `항해 중`을 더 명확한 `현재 작업 섬`으로 바꿨다.

### Fixed
- 자연어 `출항` 트리거와 항해 브리핑 계약이 설치 표면에서 빠지지 않도록 regression test를 추가했다.

## 0.0.8

### Changed
- `/sail` 진행 HUD와 최종 convergence report의 사용자-facing 라벨을 한글 중심으로 정리했다.
- 섬 수, 항해 상태, 현재 섬, 마지막 도착 섬, 진행 HUD가 `도착한 섬 수`, `항해 상태`, `현재 섬`, `마지막 도착 섬`, `진행 HUD`로 표시된다.

### Fixed
- smoke report와 `/sail` skill 문서에 영어 HUD 라벨이 다시 들어가지 않도록 회귀 테스트를 추가했다.

## 0.0.7

### Added
- `/telltale:sail`, Claude Code `/sail`, Hermes `/sail`에 이모지 항해 진행 HUD 가이드를 추가했다.
- 최종 convergence report에 `🗺️ 항해 진행` 섹션을 추가해 도착한 섬 수, 항해 상태, 현재 섬, 마지막 도착 섬을 표시하게 했다.

### Fixed
- smoke report에서 섬/항해 진행 표시가 사라지지 않도록 회귀 테스트를 추가했다.

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
