---
name: sail
description: Use when sailing toward a Telltale M1 goal.
version: 0.0.6
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
