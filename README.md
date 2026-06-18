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

There is no public `/telltale:converge` command. Convergence is the technical concept; `sail` is the user-facing command.

## Command matrix

| Environment | Command |
|---|---|
| Claude Code marketplace plugin | `/telltale:sail <task>` |
| Claude Code installed skill / local checkout alias | `/sail <task>` |
| Hermes Agent skill command | `/sail <task>` |

The short `/sail` skill is included for installed Claude Code plugins, local Claude Code development, and Hermes usage so typing `/sail` appears naturally in slash-command completion. The marketplace-safe Claude Code command remains namespaced as `/telltale:sail`.

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

Then run inside Claude Code. The canonical plugin command is namespaced, and the local checkout also provides the short alias:

```text
/telltale:sail <task>
/sail <task>
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


## Hermes Agent install

Telltale 0.0.4 adds a Hermes-native skill surface. Hermes automatically exposes installed skills as slash commands, so the skill name `sail` becomes:

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

## Troubleshooting

### Claude Code version too old

Run:

```bash
claude --version
claude update
```

Telltale 0.0.4 was validated with Claude Code 2.1.150 and Hermes skill discovery from the repository checkout.

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

Included in 0.0.4:

- Claude Code plugin manifest;
- `/telltale:sail` command and installed Claude Code `/sail` skill;
- Cartographer, Sailor, Inspector, and Advisor subagents;
- internal phase docs;
- JSON schemas for destination, island, island scorecard, event, route, report, and state;
- deterministic `scripts/telltalectl.py` helper;
- schema, event trace, state, report, and smoke validation;
- hero image and public README;
- Hermes Agent skill command support via `hermes/skills/sail` and `/sail`;
- Claude Code installed-plugin skill via `skills/sail` and local checkout alias via `.claude/commands/sail.md`, both exposing `/sail`.

## Non-goals

Telltale 0.0.4 does not implement:

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
commands/telltale-sail.md        # public /telltale:sail command
skills/sail/                     # installed Claude Code /sail skill
.claude/commands/sail.md         # Claude Code local /sail alias
agents/                          # Telltale subagents
internal/                        # M1 phase docs
schemas/                         # JSON schemas
scripts/telltalectl.py           # deterministic helper
assets/telltale-hero-monochrome.png
README.md
README.ko.md
docs/
hermes/skills/sail/              # Hermes /sail skill support
tests/
```

## License

MIT
