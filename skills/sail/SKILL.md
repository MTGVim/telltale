---
name: sail
description: 출항: Run Telltale M1 convergence.
version: 0.0.10
author: MTGVim
license: MIT
---

# Sail Skill

Use this skill when the user asks Claude Code to run Telltale, sail toward a coding goal, or apply Telltale M1's cost-aware island convergence loop.

This skill provides the short installed-plugin command:

```text
/sail <task, SOT, bug report, failing log, or goal>
```

The namespaced plugin command remains available as:

```text
/telltale:sail <task>
```

## 자연어 트리거

`/sail`은 slash command뿐 아니라 사용자가 아래처럼 말했을 때도 같은 Telltale 항해 의도로 해석한다:

- `출항`
- `출항이다`
- `이 작업 출항하자`
- `이거 Telltale로 항해하자`

자연어 트리거가 들어오면 사용자의 나머지 문장을 destination/source material로 보고, 부족하면 목표를 먼저 확인한다.

## When to Use

Use `/sail` when the user wants a bounded, evidence-backed coding loop rather than a single uninterrupted implementation pass.

Good triggers:

- `Telltale this task`
- `/sail Fix the failing search empty-state test`
- `/telltale:sail Fix the failing search empty-state test`
- `Use Telltale M1 on this bug report`
- `Map the work into islands and verify each one`
- `출항`
- `출항이다`
- `이 작업 출항하자`
- `sail this`

Do not use this skill for simple questions, one-line edits, or tasks where the user explicitly wants direct execution without Telltale's mapping and inspection overhead.

## Prerequisites

- Claude Code plugin install or local checkout of Telltale.
- A git worktree is recommended so branch-local state has a stable branch key.
- The deterministic helper is included at `scripts/telltalectl.py` inside this skill package.
- Source-of-truth references are included under `references/`.

## Quick Reference

| Telltale role | Claude Code execution surface |
|---|---|
| Orchestrator | Main Claude Code session |
| Cartographer | `@telltale-cartographer` |
| Sailor | `@telltale-sailor` scoped to current island |
| Inspector | `@telltale-inspector`; never trust Sailor self-report |
| Advisor | `@telltale-advisor` rarely for ambiguity, divergence, repeated failure, or block/abort decisions |

State paths:

```text
.claude/telltale/branches/<branch-key>/event-trace.jsonl
.claude/telltale/branches/<branch-key>/state.json
.claude/telltale/branches/<branch-key>/reports/convergence-report.md
```

## Procedure

1. **Claim loop authority.** Use the helper when available:
   ```bash
   python3 scripts/telltalectl.py init-run --input-source user_prompt
   ```

2. **Extract Destination.** Use Cartographer to produce destination id, summary, close criteria, scope, evidence, and open questions.

3. **Map Islands.** Ask Cartographer to decompose the Destination into small Islands with dependencies, close criteria, expected verification, and evidence.

4. **Score every Island.** Each scorecard must include these 0-5 fields with non-empty `basis[]` evidence:
   - `value_to_destination`
   - `cost_to_try`
   - `verification_distance`
   - `dependency_readiness`
   - `information_gain_if_fail`
   - `unknown_surface`
   - `coordination_cost`
   - `reversibility`

5. **Select the cheapest useful ready Island.** Apply:
   ```text
   usefulness = value_to_destination + information_gain_if_fail + dependency_readiness + reversibility
   cost = cost_to_try + verification_distance + unknown_surface + coordination_cost
   priority = usefulness - cost
   ```

6. **Execute current Island only.** Use Sailor. Sailor may edit code only inside current-island scope, cannot modify the island map, and cannot declare destination success.

7. **Inspect skeptically.** Use Inspector. Inspector must read actual diffs, command output, close criteria, and event trace. Inspector must not edit product code and must not trust Sailor self-report.

8. **Classify residual signals.** Record every meaningful signal as `accepted`, `deferred`, or `rejected`.

9. **Close, retry, re-chart, block, abort, or continue.** Close only with verification or an explicit recorded exception. On close, record a verified route segment.

10. **Write the report.** End with one status: `SUCCESS`, `PARTIAL`, `BLOCKED`, `ABORTED`, or `MAX_ITERATIONS`.

## 🧭 한글 항해 진행 HUD

사용자에게 `/sail` 진행 상황을 보고할 때는 짧은 이모지 HUD를 함께 쓴다. trace에 남는 machine-readable event name, status code, identifier는 그대로 두되, 사람이 읽는 라벨은 한글로 쓴다.

```text
🧭 항해: 🏝️ <도착한-섬>/<전체-섬-or-?> 도착 · ⛵ 현재 작업 섬: <현재-섬|없음> · ✅ 마지막 도착: <마지막-섬|없음> · 🎯 <SUCCESS|PARTIAL|BLOCKED|ABORTED|MAX_ITERATIONS|RUNNING>
```

권장 이모지:

| 이모지 | 의미 |
|---|---|
| 🧭 | 항해 방향 / orchestration / 다음 방향 |
| 🗺️ | 섬 지도 / 항해 진행 섹션 |
| 🏝️ | 섬 수 또는 도착한 섬 |
| ⛵ | 현재 작업 섬 / 현재 실행 |
| ✅ | 섬 닫힘 또는 최종 도착 |
| 🧪 | 검증 근거 |
| 🚧 | 막힘 또는 사용자 입력 필요 |
| 🔁 | 재항로 설정 / 재시도 |
| 🛑 | 중단 / safety stop |

예시:

```text
🧭 항해: 🏝️ 0/3 도착 · ⛵ 현재 작업 섬: island-test-log · ✅ 마지막 도착: 없음 · 🎯 RUNNING
🧭 항해: 🏝️ 1/3 도착 · ⛵ 현재 작업 섬: island-render-empty-state · ✅ 마지막 도착: island-test-log · 🎯 RUNNING
🧭 항해: 🏝️ 3/3 도착 · ⛵ 현재 작업 섬: 없음 · ✅ 마지막 도착: island-final-verify · 🎯 SUCCESS
```

## 🗺️ 지도와 브리핑 출력 계약

M1 지도는 의존관계상 독립적인 병렬 후보를 표시할 수 있지만, 기본 실행 loop는 안전하게 한 번에 하나의 현재 작업 섬만 실행한다. 병렬 후보는 지도에만 표시하고, 실제 상태라인은 항상 현재 작업 섬 하나를 기준으로 쓴다.

- `🗺️ 항해 지도`: 매핑 완료 시 전체 섬 수, 순서, 의존관계, 병렬 후보를 보여준다.
- `⛵ 출항 브리핑`: 첫 섬을 시작할 때 상태라인 1줄과 현재 작업 섬의 목표/완료 조건을 2~4줄로 요약한다.
- `✅ 섬 완료 브리핑`: 섬 하나가 검증으로 닫힐 때 상태라인 1줄과 완료 근거/다음 섬을 2~4줄로 요약한다.
- `🏁 최종 도착 브리핑`: 전체 완료 시 상태라인 1줄과 최종 결과/검증/산출물/남은 위험을 요약한다.

지도는 처음 한 번 상세히 보여주고, 이후에는 재항로 설정이나 의존관계 변경이 있을 때만 다시 보여준다. 브리핑은 길게 늘리지 말고, 사용자가 중간에 들어와도 현재 위치를 바로 알 수 있을 정도로만 쓴다.

## Pitfalls

- Do not let Sailor expand scope or edit the island map.
- Do not let Inspector rely on Sailor's summary as primary evidence.
- Do not close an island without verification unless the exception is explicit in the event trace.
- Do not re-litigate deferred/rejected signals unless new evidence invalidates the previous decision.

## Verification

For repo development, run:

```bash
python3 scripts/telltalectl.py validate-schemas
python3 scripts/telltalectl.py smoke
python3 -m unittest discover -s tests -v
```

The work is complete only when the final report lists real verification output or clearly marks any check as NOT RUN with the exact reason.
