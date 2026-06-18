## close-island.md

# Close Island

See `island-close.md` for the M1 island close contract.

## current-island-execution.md

# Current Island Execution

Sailor executes only the selected current Island.

Rules:
- Sailor may edit product code only within the Island scope.
- Sailor must not modify the island map.
- Sailor must not declare Destination success.
- If work exceeds scope, Sailor stops and reports a signal.
- Append `sailor_result` with files changed, commands run, blockers, and unexpected signals.

## destination-extraction.md

# Destination Extraction

Cartographer converts the user's task, SOT, bug report, or failing log into a concrete Destination.

Required output:
- destination id and concise statement;
- close criteria;
- source evidence;
- explicit exclusions;
- unresolved questions.

Rules:
- Do not infer hidden acceptance criteria.
- Missing source-of-truth evidence must be recorded as uncertainty.
- Append `destination_extracted` before island mapping.

## island-close.md

# Island Close

Orchestrator decides whether an Island can close.

Close requires:
- Inspector close recommendation;
- passing verification or an explicit recorded exception;
- no accepted residual that invalidates close criteria.

On close, append `island_reached` and `verified_route_recorded`. Route segments include facts, decisions, constraints, passed checks, deferred signals, and rejected signals.

## island-map.md

# Island Map

Cartographer decomposes the Destination into candidate Islands.

Each Island must include:
- id;
- title;
- scope;
- dependencies;
- close criteria;
- evidence;
- expected verification.

Rules:
- Islands should be small enough for Sailor to execute without scope drift.
- Do not include roadmap/future work in M1 islands unless required by the current Destination.
- Append `island_map_created` after mapping.

## island-scorecard.md

# Island Scorecard

Every Island must be scored on the fixed 0-5 M1 scale.

Fields:
- `value_to_destination`
- `cost_to_try`
- `verification_distance`
- `dependency_readiness`
- `information_gain_if_fail`
- `unknown_surface`
- `coordination_cost`
- `reversibility`

Every score must include non-empty `basis[]`. Unsupported confidence is forbidden. Missing evidence increases `unknown_surface`.

## island-select.md

# Island Selection

See `island-selection.md` for the M1 cheapest-useful-island selection contract.

## island-selection.md

# Island Selection

Select the cheapest useful ready Island.

Formula:

```text
usefulness = value_to_destination + information_gain_if_fail + dependency_readiness + reversibility
cost = cost_to_try + verification_distance + unknown_surface + coordination_cost
priority = usefulness - cost
```

Selection rules:
1. Remove islands with `value_to_destination <= 0`.
2. Defer islands with `dependency_readiness == 0`.
3. Split islands with `verification_distance >= 4`.
4. Split islands with `unknown_surface >= 4` unless `information_gain_if_fail` is high.
5. Select the ready island with highest priority.
6. On ties, choose lower cost.
7. If all priorities are low, re-chart or ask Advisor/user.

## re-chart.md

# Re-chart

Re-chart when drift, ambiguity, accepted residuals, repeated failure, changed Destination, or contradictory verification invalidates the route.

Rules:
- Prefer smaller re-charting over expanding scope.
- Advisor is required for repeated failure, oscillation, low confidence, or block/abort uncertainty.
- Append `island_recharted` with invalidated route segments and the new candidate map.

## rechart.md

# Re-chart

See `re-chart.md` for the M1 re-chart contract.

## report.md

# Report

The convergence report is a human-readable summary derived from the event trace.

It must include:
- final status;
- destination;
- reached islands;
- verified route segments;
- deferred/rejected signals;
- verification commands and results;
- blockers or caveats;
- next recommended action.

Append `convergence_report_written`, then `loop_authority_released`.

## residual-inspection.md

# Residual Inspection

Inspector verifies Sailor output skeptically.

Inputs:
- current Island close criteria;
- git diff;
- command/test output;
- event trace;
- Sailor report as secondary evidence only.

Inspector must identify what passed, failed, remains unknown, or drifted. Append `verification_result` and `inspector_residual`.

## signal-classification.md

# Signal Classification

Signals are findings from Sailor or Inspector.

Classes:
- `accepted`: affects the current island or verified route now;
- `deferred`: useful but outside current island;
- `rejected`: duplicate, speculative, preference-only, or convention-handled.

Meaningful does not automatically mean in scope. Deferred/rejected signals must still be recorded to prevent repeated debate.
