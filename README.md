# Telltale

[![Validate](https://github.com/MTGVim/telltale/actions/workflows/validate.yml/badge.svg)](https://github.com/MTGVim/telltale/actions/workflows/validate.yml)

![Telltale hero](assets/telltale-hero-monochrome.png)

Telltale is a Claude Code plugin for cost-aware island convergence. It helps long-running agentic work avoid drift by decomposing a destination into small evidence-scored islands, sailing to the cheapest useful ready island, verifying it skeptically, and carrying forward only verified route segments.

```text
Win small, or learn cheap.
```

Current release: `0.0.7`.

## When to use

Use Telltale when:
- the task is long-running;
- scope drift is likely;
- verification must be evidence-based, not self-reported;
- you want the agent to finish one bounded island before expanding scope;
- failed attempts should leave useful route information rather than transcript noise.

## When not to use

Do not use Telltale when:
- the task is a tiny one-shot edit;
- you already know the exact file and patch;
- exploration cost is higher than direct implementation;
- you need a background daemon or cross-run learning system.

## `/goal` comparison

`/goal` defines done.

`/telltale:sail` controls the route.

Use `/goal` for the destination contract. Use `/telltale:sail` when the route may drift.

```text
/goal The checkout bug is fixed when empty carts show a helpful state and tests pass.
/telltale:sail Fix the checkout empty-cart state from the current failing test log.
```

## Commands

Telltale exposes exactly one marketplace-safe public Claude Code command:

```text
/telltale:sail <task, SOT, bug report, failing log, or goal>
```

The short `/sail` skill is included for installed Claude Code plugins, local Claude Code development, and Hermes usage:

| Environment | Command |
|---|---|
| Claude Code marketplace plugin | `/telltale:sail <task>` |
| Claude Code installed skill / local checkout alias | `/sail <task>` |
| Hermes Agent skill command | `/sail <task>` |

There is no public `/telltale:converge` command. Convergence is the technical concept; `sail` is the user-facing command.

## What Telltale does

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

For a concrete miniature run, see [`docs/examples/fix-failing-test.md`](docs/examples/fix-failing-test.md).

Telltale user-facing progress uses a compact route HUD, for example:

```text
🧭 항해: 🏝️ 2/4 도착 · ⛵ 현재 작업 섬: island-render-empty-state · ✅ 마지막 도착: island-test-log · 🎯 RUNNING
```

## Claude Code local development install

```bash
git clone https://github.com/MTGVim/telltale.git
cd telltale
claude --plugin-dir .
```

Then run inside Claude Code:

```text
/telltale:sail <task>
/sail <task>
```

Local validation:

```bash
npm run validate
python3 scripts/telltalectl.py doctor
```

`npm run validate` includes `claude plugin validate . --strict`, schema validation, smoke validation, doctor diagnostics, and unit tests.

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

A plain Git URL also works for adding the marketplace:

```text
/plugin marketplace add https://github.com/MTGVim/telltale.git
```

## Hermes Agent install

Telltale 0.0.7 includes a Hermes-native skill surface. Hermes automatically exposes installed skills as slash commands, so the skill name `sail` becomes:

```text
/sail <task, SOT, bug report, failing log, or goal>
```

From a checkout of this repository, install or inspect the skill from:

```text
hermes/skills/sail/SKILL.md
```

For local development, copy or symlink that directory into your active Hermes profile's skills directory, then start a fresh Hermes session so command discovery can rescan skills:

```bash
mkdir -p "${HERMES_HOME:-$HOME/.hermes}/skills"
ln -sfn "$(pwd)/hermes/skills/sail" "${HERMES_HOME:-$HOME/.hermes}/skills/sail"
hermes -s sail
```

Then use:

```text
/sail Fix the search empty state bug and verify it.
```

This is native Hermes skill-command support, not a Hermes core slash-command patch. The same short `/sail` spelling is also available as a Claude Code local checkout alias; the Claude Code marketplace command remains `/telltale:sail`.

## Verify installation

Run:

```bash
python3 scripts/telltalectl.py doctor
```

Healthy output looks like:

```text
Telltale doctor

OK   plugin manifest found
OK   marketplace manifest found
OK   public command found: /telltale:sail
OK   local alias found: /sail
OK   Hermes skill found: hermes/skills/sail
OK   generated state is gitignored
OK   versions match: 0.0.10

Result: healthy
```

## Troubleshooting

### Claude Code version too old

Run:

```bash
claude --version
claude update
```

Telltale 0.0.7 was validated with Claude Code 2.1.150 and Hermes skill discovery from the repository checkout.

### `/plugin` command missing

Your Claude Code build is too old or plugin support is disabled. Update Claude Code and restart the session.

### `/telltale:sail` namespace not visible

Check:

```bash
claude plugin validate . --strict
python3 scripts/telltalectl.py doctor
claude --plugin-dir .
```

Then run `/reload-plugins` in Claude Code and check `/help` or slash-command completion for `/telltale:sail`.

### `/sail` alias not visible

Check that one of these surfaces is installed or loaded:

```text
skills/sail/
.claude/commands/sail.md
hermes/skills/sail/SKILL.md
```

Then reload the host session.

### Schema validation failure

Run:

```bash
python3 scripts/telltalectl.py validate-schemas
python3 scripts/telltalectl.py doctor
```

The helper resolves schemas from the installed package/repository and writes state under the current project.
It should not create or require `schemas/` inside your project; generated user-project state belongs under `.claude/telltale/` only.

### Generated state appears in git

`.claude/telltale/` is generated branch-local state and should stay untracked. This repo includes it in `.gitignore`; `doctor` checks this coverage.

### GitHub marketplace not refreshed

Run:

```text
/plugin marketplace update telltale
/reload-plugins
```

If needed, remove and re-add the marketplace source.

## M1 scope

Included in 0.0.7:

- Claude Code plugin manifest;
- `/telltale:sail` command and installed Claude Code `/sail` skill;
- Cartographer, Sailor, Inspector, and Advisor subagents;
- internal phase docs;
- JSON schemas for destination, island, island scorecard, event, route, report, and state;
- deterministic `scripts/telltalectl.py` helper;
- schema, event trace, state, report, smoke, doctor, and unit validation;
- CI validation workflow;
- example-driven first-run documentation;
- Hermes Agent skill command support via `hermes/skills/sail` and `/sail`;
- Claude Code installed-plugin skill via `skills/sail` and local checkout alias via `.claude/commands/sail.md`, both exposing `/sail`.

## Non-goals

Telltale 0.0.7 does not implement:

- meta-feedback;
- loop-memory or cross-run learning;
- model-routing UI;
- worktree isolation;
- automatic rule promotion;
- background daemons;
- new public command `/telltale:converge`.

## Repository layout

```text
.claude-plugin/plugin.json       # Claude Code plugin manifest
.claude-plugin/marketplace.json  # repo-local marketplace manifest
.github/workflows/validate.yml   # GitHub Actions validation
commands/telltale-sail.md        # public /telltale:sail command
skills/sail/                     # installed Claude Code /sail skill
.claude/commands/sail.md         # Claude Code local /sail alias
agents/                          # Telltale subagents
internal/                        # M1 phase docs
schemas/                         # JSON schemas
scripts/telltalectl.py           # deterministic helper + doctor
assets/telltale-hero-monochrome.png
CHANGELOG.md
docs/
hermes/skills/sail/              # Hermes /sail skill support
tests/
```

## Release

See [`CHANGELOG.md`](CHANGELOG.md) and [`docs/release-checklist.md`](docs/release-checklist.md).

## License

MIT
