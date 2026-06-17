---
description: Alias for Telltale's cost-aware island convergence loop.
argument-hint: "<task, SOT, bug report, failing log, or goal>"
---

# /sail

This is the repo-local Claude Code short alias for Telltale.

Run the same M1 behavior as the plugin command `/telltale:sail`:

- extract the Destination;
- map evidence-backed Islands;
- score every Island;
- select the cheapest useful ready Island;
- use Sailor only for the current Island;
- use Inspector to verify with evidence and distrust self-report;
- call Advisor rarely for ambiguity, divergence, repeated failure, or block/abort uncertainty;
- maintain `.claude/telltale/branches/<branch-key>/event-trace.jsonl` as the source of truth;
- derive state and write a convergence report.

Delegate to the canonical command contract in `commands/sail.md` and the M1 references in `docs/RFC_TELLTALE_M1.md` and `docs/HERMES_IMPLEMENTATION_BRIEF.md`.

User task:

```text
$ARGUMENTS
```
