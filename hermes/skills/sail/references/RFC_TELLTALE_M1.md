# RFC: Telltale M1 — Cost-aware Island Convergence for Claude Code

## Status

Draft v0.1

## Summary

Telltale is a bounded convergence orchestrator for Claude Code.

M1 provides one public command:

```txt
/telltale:sail
```

The command turns user intent, SOT, bug reports, or failing logs into a cost-aware island convergence loop.

```txt
destination extraction
→ island map
→ island scorecard
→ cheapest useful island selection
→ Sailor execution
→ Inspector verification/residual analysis
→ island close / re-chart / stop
→ convergence report
```

M1 focuses only on the convergence loop. It does not include meta-feedback, loop-memory, doctor diagnostics, worktree isolation, or automatic rule promotion.

---

## Core thesis

Agentic coding does not fail just because the goal is unclear.

It fails because the run drifts.

Telltale does not try to know the safest route upfront. Safety is not known until the run reaches the island.

Instead, Telltale picks the cheapest useful island:

- if it succeeds, it leaves a verified route;
- if it fails, it leaves evidence that narrows the next voyage.

```txt
Win small, or learn cheap.
```

---

## Non-goals

M1 is not:

- a general agent OS;
- a background daemon;
- a team/tmux worker manager;
- a provider bridge;
- an always-run-until-done autopilot;
- a cross-run learning system;
- a meta-feedback generator.

---

## Namespace

Public command:

```txt
/telltale:sail
```

Generated state:

```txt
.claude/telltale/
```

Command source:

```txt
commands/sail.md
.claude-plugin/plugin.json
```

M1 manifest:

```json
{
  "commands": [
    "./commands/sail.md"
  ]
}
```

---

## Agent architecture

M1 uses real subagents.

| Agent | Responsibility | Suggested model tier |
|---|---|---|
| Orchestrator | Controls the run, selects islands, records events, decides state | main / standard |
| Cartographer | Extracts destination and builds evidence-backed island map | standard |
| Sailor | Executes only the current island | cheap by default for simple islands |
| Inspector | Verifies Sailor output using diff, verification, close criteria | standard, not weaker than Sailor |
| Advisor | Reviews ambiguity, divergence, re-charting, block/abort decisions | high, rare |

Core rule:

```txt
Sailor may be cheap.
Inspector must be skeptical.
Advisor is expensive and rare.
```

---

## Island scorecard

Every island must be scored on a fixed 0–5 scale.

Each field must include `score` and `basis[]`.

Fields:

- `value_to_destination`
- `cost_to_try`
- `verification_distance`
- `dependency_readiness`
- `information_gain_if_fail`
- `unknown_surface`
- `coordination_cost`
- `reversibility`

Priority formula:

```txt
usefulness =
  value_to_destination
+ information_gain_if_fail
+ dependency_readiness
+ reversibility

cost =
  cost_to_try
+ verification_distance
+ unknown_surface
+ coordination_cost

priority = usefulness - cost
```

Selection rules:

1. Remove islands with `value_to_destination <= 0`.
2. Defer islands with `dependency_readiness == 0`.
3. Split islands with `verification_distance >= 4`.
4. Split islands with `unknown_surface >= 4` unless `information_gain_if_fail` is also high.
5. Select the ready island with highest priority.
6. On ties, choose lower cost.
7. If all priorities are low, re-chart or ask Advisor/user.

Unsupported confidence is not allowed. Missing evidence increases `unknown_surface`.

---

## Verified route carry-forward

When an island closes, it emits a verified route segment.

A verified route segment contains:

- facts;
- decisions;
- constraints;
- passed checks;
- deferred signals;
- rejected signals.

Later islands must consume verified route segments unless invalidated.

Invalidation triggers:

- destination changed;
- current island scope changed;
- new verification failure contradicts route;
- user/advisor reverses prior decision;
- repository state changes outside the run.

---

## Signal classification

Signals are findings produced by Sailor or Inspector.

Signal classes:

- `accepted`: must affect the current island or route;
- `deferred`: useful but outside the current island;
- `rejected`: duplicate, speculative, preference-only, or convention-handled.

Rules:

- Meaningful does not automatically mean in scope.
- Repeated signals reuse prior decisions unless new evidence invalidates them.
- Deferred/rejected signals must still be recorded to prevent repeated debate.

---

## Event trace

The event trace is append-only.

Default path:

```txt
.claude/telltale/branches/<branch-key>/event-trace.jsonl
```

Derived state:

```txt
.claude/telltale/branches/<branch-key>/state.json
```

Report:

```txt
.claude/telltale/branches/<branch-key>/reports/convergence-report.md
```

Required M1 events:

- `run_started`
- `loop_authority_claimed`
- `destination_extracted`
- `island_map_created`
- `island_scored`
- `island_selected`
- `island_started`
- `sailor_result`
- `verification_result`
- `inspector_residual`
- `signal_classified`
- `island_reached`
- `verified_route_recorded`
- `island_recharted`
- `run_blocked`
- `run_aborted`
- `max_iterations_reached`
- `convergence_report_written`
- `loop_authority_released`

---

## Loop authority

Only one active Telltale convergence run may own the workspace at a time.

If a new run starts while one is active, Orchestrator must choose:

- resume current run;
- abort current run;
- write report and stop;
- explicitly start a new run.

---

## Termination

Telltale ends with one of:

- `SUCCESS`
- `PARTIAL`
- `BLOCKED`
- `ABORTED`
- `MAX_ITERATIONS`

Default M1 budgets:

```txt
max_total_iterations: 20
max_island_iterations: 3
max_recharts: 5
max_repeated_failure: 3
```

---

## Anti-hallucination rules

1. No island score without evidence.
2. Missing evidence increases `unknown_surface`.
3. Sailor cannot modify the island map.
4. Sailor cannot declare destination success.
5. Inspector cannot edit product code.
6. Inspector must use diff, verification output, close criteria, and event trace.
7. Advisor recommends; Orchestrator decides.
8. No verification, no island close, unless explicit exception is recorded.
9. Prior decisions are reused unless invalidated.
10. Repeated failure, oscillation, scope expansion, and low-confidence re-chart require Advisor or user input.

---

## Acceptance criteria

M1 is complete when:

1. `/telltale:sail` exists as the only public command.
2. It creates a destination from user input.
3. It creates an island map.
4. Each island has an evidence-backed scorecard.
5. It selects the cheapest useful ready island.
6. Sailor executes only the current island.
7. Inspector verifies Sailor output using evidence.
8. Signals are classified as accepted/deferred/rejected.
9. Reached islands emit verified route segments.
10. Verified route segments carry forward to later islands.
11. Prior decisions are reused unless invalidated.
12. Re-chart happens on drift, ambiguity, or repeated failure.
13. Event trace is append-only and branch-local.
14. State is derived from event trace.
15. Final convergence report is written.
16. Termination status is one of SUCCESS, PARTIAL, BLOCKED, ABORTED, MAX_ITERATIONS.
17. No meta-feedback, loop-memory, model routing UI, doctor, or worktree isolation is required for M1.

---

## Core definition

Telltale M1 is a cost-aware greedy island convergence loop.

It decomposes noisy Claude Code work into evidence-scored islands, chooses the cheapest useful island, executes it with a scoped Sailor, verifies it with a skeptical Inspector, records every material event, carries forward verified routes, and re-charts when the run drifts.
