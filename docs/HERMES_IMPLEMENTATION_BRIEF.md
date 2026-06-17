# Hermes Implementation Brief: Telltale M1

You are implementing Telltale M1.

Do not implement the whole future roadmap. Build the M1 core only.

## Goal

Implement a Claude Code plugin with exactly one public command:

```txt
/telltale:sail
```

The command runs a cost-aware greedy island convergence loop.

## Required public surface

```txt
/telltale:sail
```

No `/telltale:meta-feedback`, no `/telltale:doctor`, no `/telltale:handoff`, no debug phase commands for M1.

## Required files

Create or update:

```txt
.claude-plugin/plugin.json
commands/sail.md
agents/telltale-cartographer.md
agents/telltale-sailor.md
agents/telltale-inspector.md
agents/telltale-advisor.md
internal/island-scorecard.md
internal/island-select.md
internal/close-island.md
internal/rechart.md
internal/report.md
schemas/destination.schema.json
schemas/island.schema.json
schemas/island-scorecard.schema.json
schemas/event.schema.json
schemas/route.schema.json
schemas/report.schema.json
schemas/state.schema.json
scripts/telltalectl.py
README.md
```

## Required behavior

1. `/telltale:sail` receives user input or SOT.
2. Orchestrator claims loop authority.
3. Cartographer extracts a destination.
4. Cartographer builds an island map.
5. Every island has an evidence-backed scorecard.
6. Orchestrator selects the cheapest useful ready island.
7. Sailor executes only current island.
8. Inspector verifies Sailor output using diff and verification output.
9. Inspector classifies signals.
10. Orchestrator closes island, re-charts, retries, blocks, aborts, or completes.
11. Reached islands emit verified route segments.
12. Verified route carries forward to later islands.
13. All material events are appended to `.claude/telltale/branches/<branch-key>/event-trace.jsonl`.
14. State is reduced from event trace.
15. Convergence report is written.

## Critical constraints

- Sailor must not modify the island map.
- Sailor must not declare destination success.
- Inspector must not trust Sailor self-report.
- Inspector must not edit product code.
- Advisor recommends only.
- Orchestrator decides.
- Every score requires basis.
- Missing evidence increases `unknown_surface`.
- No island close without verification unless explicit exception is recorded.

## Model policy

Use subagent frontmatter where supported.

- Cartographer: standard model
- Sailor: cheap model by default
- Inspector: standard model, not weaker than Sailor for non-trivial islands
- Advisor: high model, called rarely

If exact model aliases are unavailable in target environment, keep relative policy in comments/frontmatter.

## Do not implement in M1

- meta-feedback
- loop-memory
- cross-run learning
- doctor diagnostics
- evidence content-hash anchors
- model routing UI
- strict/economy mode flags
- worktree isolation
- automatic rule promotion

## Success criteria

The implementation is acceptable when a user can run:

```txt
/telltale:sail Fix the search empty state bug and verify it.
```

and Telltale produces:

- destination;
- island map;
- selected current island;
- Sailor result;
- Inspector result;
- event trace;
- convergence report;
- clear termination status.
