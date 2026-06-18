---
description: 출항: alias for Telltale island convergence.
argument-hint: "<task, SOT, bug report, failing log, or goal>"
---

# /sail

This is the repo-local Claude Code short alias for Telltale.

Run the same M1 behavior as the plugin command `/telltale:sail`:

## 자연어 트리거

이 repo-local alias는 아래 자연어 요청도 `/sail` 의도로 안내한다:

- `출항`
- `출항이다`
- `이 작업 출항하자`
- `이거 Telltale로 항해하자`


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
