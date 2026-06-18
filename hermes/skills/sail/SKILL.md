---
name: sail
description: Run Telltale M1 convergence in Hermes.
version: 0.0.7
author: MTGVim
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telltale, convergence, coding, workflow]
    category: software-development
    related_skills: [claude-code, test-driven-development]
---

# Sail Skill

Use this skill when the user asks Hermes to run Telltale, sail toward a coding goal, or apply Telltale M1's cost-aware island convergence loop. This is the Hermes-native skill surface for Telltale; the Claude Code marketplace command remains `/telltale:sail`.

The skill exposes Hermes' automatic slash command:

```text
/sail <task, SOT, bug report, failing log, or goal>
```

## When to Use

Use `/sail` when the user wants a bounded, evidence-backed coding loop rather than a single uninterrupted implementation pass.

Good triggers:

- `Telltale this task`
- `/sail Fix the failing search empty-state test`
- `Use Telltale M1 on this bug report`
- `Map the work into islands and verify each one`
- `출항`
- `출항이다`
- `이 작업 출항하자`
- `sail this`

Do not use this skill for simple questions, one-line edits, or tasks where the user explicitly wants direct execution without Telltale's mapping and inspection overhead.

## Prerequisites

- Hermes toolsets: `terminal`, `file`, and `delegation` are recommended.
- A git worktree is recommended so branch-local state has a stable branch key.
- The deterministic helper is included at `scripts/telltalectl.py` inside this skill package.
- Source-of-truth references are included under `references/`.

If the helper file is not available after a remote skill install, continue with the written M1 procedure and tell the user helper validation is unavailable in that install mode.

## How to Run

From an interactive Hermes session:

```text
/sail Fix the search empty state bug and verify it.
```

If the skill is loaded by name instead of slash command:

```text
Use the sail skill on: Fix the search empty state bug and verify it.
```

## Quick Reference

| Telltale role | Hermes execution surface |
|---|---|
| Orchestrator | Main Hermes agent |
| Cartographer | `delegate_task` with `file`/`terminal` tools |
| Sailor | `delegate_task` or direct Hermes tool use scoped to current island |
| Inspector | Separate `delegate_task`; never trust Sailor self-report |
| Advisor | Rare `delegate_task` for ambiguity, divergence, repeated failure, or block/abort decisions |

State paths stay compatible with the Claude Code plugin:

```text
.claude/telltale/branches/<branch-key>/event-trace.jsonl
.claude/telltale/branches/<branch-key>/state.json
.claude/telltale/branches/<branch-key>/reports/convergence-report.md
```

## Procedure

1. **Claim loop authority.** Use `terminal` to run the helper when available:
   ```bash
   python3 <skill-dir>/scripts/telltalectl.py init-run --input-source user_prompt
   ```
   If the installed skill path is not known, create the `.claude/telltale/` event trace manually and record that helper execution was unavailable.

2. **Extract Destination.** Use `delegate_task` as Cartographer, passing the user task and asking for:
   - destination id and summary;
   - close criteria;
   - in-scope and out-of-scope items;
   - evidence and open questions.

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
   Drop zero-value islands, defer dependency-blocked islands, split high verification-distance islands, and split high unknown-surface islands unless failure would produce high information gain.

6. **Execute current Island only.** Use Sailor as a separate `delegate_task` when the work is non-trivial. Sailor may edit code only inside current-island scope. Sailor cannot modify the island map or declare destination success.

7. **Inspect skeptically.** Use Inspector as a separate `delegate_task`. Inspector must read actual diffs, command output, close criteria, and the event trace. Inspector must not edit product code and must not trust Sailor self-report.

8. **Classify residual signals.** Record every meaningful signal as:
   - `accepted`: affects current island or route now;
   - `deferred`: useful but outside current island;
   - `rejected`: duplicate, speculative, preference-only, or convention-handled.

9. **Close, retry, re-chart, block, abort, or continue.** Close only with verification or an explicit recorded exception. On close, record a verified route segment with facts, decisions, constraints, passed checks, deferred signals, and rejected signals.

10. **Write the report.** End with one status: `SUCCESS`, `PARTIAL`, `BLOCKED`, `ABORTED`, or `MAX_ITERATIONS`. Report the destination, reached islands, checks, route segments, unresolved caveats, and next action.

## Emoji Route Progress

User-facing `/sail` progress should use a compact route HUD whenever reporting mapping, current-island execution, island close, re-chart, block, abort, or final report status. Keep machine-readable event names and status codes unchanged, but make the human progress line visually scannable:

```text
🧭 Route: 🏝️ <reached>/<mapped-or-?> reached · ⛵ sailing: <current-island|none> · ✅ last island: <last-reached|none> · 🎯 <SUCCESS|PARTIAL|BLOCKED|ABORTED|MAX_ITERATIONS|RUNNING>
```

Recommended glyphs:

| Glyph | Meaning |
|---|---|
| 🧭 | route / orchestration / next direction |
| 🗺️ | island map / route progress section |
| 🏝️ | island count or reached island |
| ⛵ | currently sailing / current island execution |
| ✅ | island closed or final destination reached |
| 🧪 | verification evidence |
| 🚧 | blocked or needs input |
| 🔁 | re-chart / retry |
| 🛑 | abort / safety stop |

Examples:

```text
🧭 Route: 🏝️ 0/3 reached · ⛵ sailing: island-test-log · ✅ last island: none · 🎯 RUNNING
🧭 Route: 🏝️ 1/3 reached · ⛵ sailing: island-render-empty-state · ✅ last island: island-test-log · 🎯 RUNNING
🧭 Route: 🏝️ 3/3 reached · ⛵ sailing: none · ✅ last island: island-final-verify · 🎯 SUCCESS
```

## Pitfalls

- Do not let Sailor expand scope or edit the island map.
- Do not let Inspector rely on Sailor's summary as primary evidence.
- Do not close an island without verification unless the exception is explicit in the event trace.
- Do not re-litigate deferred/rejected signals unless new evidence invalidates the previous decision.
- Do not claim native Claude Code command behavior inside Hermes; Hermes uses `/sail` as a skill command.

## Verification

When the helper is available, verify with `terminal`:

```bash
python3 <skill-dir>/scripts/telltalectl.py validate-schemas
python3 <skill-dir>/scripts/telltalectl.py smoke
```

For repo development, run from the Telltale repository root:

```bash
python3 scripts/telltalectl.py validate-schemas
python3 scripts/telltalectl.py smoke
python3 -m unittest discover -s tests -v
```

The work is complete only when the final report lists real verification output or clearly marks any check as NOT RUN with the exact reason.
