# Artifacts and Event Trace

Telltale의 기억은 숨은 model state가 아니다.

```txt
event trace = source of truth
state = derived cache
report = human-readable summary
```

## Generated state

```txt
.claude/telltale/
  branches/
    <branch-key>/
      event-trace.jsonl
      state.json
      destination.md
      islands/
      routes/
      verification/
      reports/
```

## Required events

- run_started
- loop_authority_claimed
- destination_extracted
- island_map_created
- island_scored
- island_selected
- island_started
- sailor_result
- verification_result
- inspector_residual
- signal_classified
- island_reached
- verified_route_recorded
- island_recharted
- run_blocked
- run_aborted
- max_iterations_reached
- convergence_report_written
- loop_authority_released
