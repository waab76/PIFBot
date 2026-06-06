# PIFBot
Reddit bot automating giveaways (PIFs) on r/Wetshaving.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --dev
```

- Reddit credentials: `praw.ini` with section `[PIFBot]` (gitignored)
- Bot config: `config.py` (gitignored) — blacklist, log path, monitored subreddits

## Run

```bash
uv run python3 pifbot.py
```

Spawns 5 daemon threads monitoring submissions, comments, edits, and private messages.

## Pre-commit checks

Run manually (all files):
```bash
uv run pre-commit run --all-files
```

Install as a git hook to run automatically on every commit:
```bash
uv run pre-commit install
```

Once installed, the hook runs trailing-whitespace, end-of-file-fixer, YAML/TOML validation, ruff (lint + format), mypy, and pytest before each commit.
