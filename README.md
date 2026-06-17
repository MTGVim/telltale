# Telltale

![Telltale hero](assets/telltale-hero-monochrome.png)

Telltale is a Claude Code plugin for cost-aware island convergence. It helps long-running agentic work avoid drift by decomposing a destination into small evidence-scored islands, sailing to the cheapest useful ready island, verifying it skeptically, and carrying forward only verified route segments.

```text
Win small, or learn cheap.
```

## Project concept

Agentic coding does not fail only because goals are unclear. It often fails because the run drifts: a useful-looking tangent expands scope, verification becomes self-report, or previous decisions get re-litigated.

Telltale M1 keeps the loop bounded:

1. extract a destination;
2. map candidate islands;
3. score every island with evidence;
4. select the cheapest useful ready island;
5. let Sailor execute only that island;
6. let Inspector verify with evidence, not trust;
7. classify residual signals;
8. close, re-chart, block, abort, or continue;
9. write an event trace, derived state, and report.

Generated state is branch-local and lives under `.claude/telltale/`. It is intentionally gitignored.

## `/goal` comparison

`/goal` is a broad completion contract: it tells an agent what "done" means.

`/telltale:sail` is a convergence control loop: it decides which small island is worth trying next, records the result, and carries verified route segments forward.

Use them together when helpful:

```text
/goal The checkout bug is fixed when empty carts show a helpful state and tests pass.
/telltale:sail Fix the checkout empty-cart state from the current failing test log.
```

## Public command

Telltale exposes exactly one public command:

```text
/telltale:sail <task, SOT, bug report, failing log, or goal>
```

There is no public `/telltale:converge` command in 0.0.1. Convergence is the technical concept; `sail` is the user-facing command.

## Usage

Inside Claude Code after loading or installing the plugin:

```text
/telltale:sail Fix the search empty state bug and verify it.
```

Telltale will guide Claude through Cartographer, Sailor, Inspector, and rare Advisor phases. The orchestrator remains responsible for decisions and event recording.

## Claude Code local development install

```bash
git clone https://github.com/MTGVim/telltale.git
cd telltale
claude --plugin-dir .
```

Then run inside Claude Code:

```text
/telltale:sail <task>
```

Local validation:

```bash
claude plugin validate . --strict
python3 scripts/telltalectl.py validate-schemas
python3 scripts/telltalectl.py smoke
python3 -m unittest discover -s tests -v
```

## Claude Code marketplace/public install

This repository includes `.claude-plugin/marketplace.json`, so users can add the repository as a marketplace source and install the `telltale` plugin from it.

Inside Claude Code:

```text
/plugin marketplace add MTGVim/telltale
/plugin install telltale@telltale
/reload-plugins
/telltale:sail <task>
```

The local command equivalent is:

```bash
claude plugin marketplace add MTGVim/telltale
claude plugin install telltale@telltale
```

This was verified against Claude Code 2.1.150 in an isolated HOME. A plain Git URL also works for adding the marketplace:

```text
/plugin marketplace add https://github.com/MTGVim/telltale.git
```

## Troubleshooting

### Claude Code version too old

Run:

```bash
claude --version
claude update
```

Telltale 0.0.1 was validated with Claude Code 2.1.150.

### `/plugin` command missing

Your Claude Code build is too old or plugin support is disabled. Update Claude Code and restart the session.

### `/telltale:sail` namespace not visible

Check:

```bash
claude plugin validate . --strict
claude --plugin-dir .
```

Then run `/reload-plugins` in Claude Code and check `/help` or slash-command completion for `/telltale:sail`.

### Generated state appears in git

`.claude/telltale/` is generated branch-local state and should stay untracked. This repo includes it in `.gitignore`.

### GitHub marketplace not refreshed

Run:

```text
/plugin marketplace update telltale
/reload-plugins
```

If needed, remove and re-add the marketplace source.

## M1 scope

Included in 0.0.1:

- Claude Code plugin manifest;
- `/telltale:sail` command;
- Cartographer, Sailor, Inspector, and Advisor subagents;
- internal phase docs;
- JSON schemas for destination, island, island scorecard, event, route, report, and state;
- deterministic `scripts/telltalectl.py` helper;
- schema, event trace, state, report, and smoke validation;
- hero image and public README.

## Non-goals

Telltale 0.0.1 does not implement:

- meta-feedback;
- loop-memory or cross-run learning;
- model-routing UI;
- worktree isolation;
- automatic rule promotion;
- background daemons;
- doctor diagnostics.

## Repository layout

```text
.claude-plugin/plugin.json       # Claude Code plugin manifest
.claude-plugin/marketplace.json  # repo-local marketplace manifest
commands/sail.md                 # public /telltale:sail command
agents/                          # Telltale subagents
internal/                        # M1 phase docs
schemas/                         # JSON schemas
scripts/telltalectl.py           # deterministic helper
assets/telltale-hero-monochrome.png
README.md
README.ko.md
docs/
tests/
```

## License

MIT
