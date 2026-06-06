# Codebase Modernization — Design Spec

**Date:** 2026-06-06
**Project:** PIFBot / LatherBot
**Goal:** Modernize a 6-year-old Python Reddit bot to 2026 standards via short topic branches, each independently mergeable to master.

## Execution Model

12 short-lived topic branches, each 1-3 days, merging to master as completed. Branches 1-6 are low-risk (infra, bugfixes, dead code removal, config changes). Branches 7-10 are high-touch (type annotations, Pydantic models). Branches 11-12 are additive (tests).

## Branch Sequence

### 1. `tooling`
**pyproject.toml**, uv, ruff, mypy. No code changes — pure additive infra.

- `pyproject.toml` with project metadata, python requires >=3.11
- Ruff config: line-length 88, select E/F/I/UP/B/SIM, Google-style docstrings
- MyPy: strict mode, `ignore_errors = true` on all existing modules initially
- `uv.lock` and `.python-version` committed
- No `requirements.txt` — replaced by uv
- `.pre-commit-config.yaml` modeled on `mission-control`: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-merge-conflict, check-added-large-files, ruff, ruff-format, mypy, pytest.
- `pre-commit` added as a dev dependency via `uv add --dev pre-commit`.
- Run manually: `uv run pre-commit run --all-files`.
- Do **not** install the git hook yet — checks won't pass until later branches. Document `uv run pre-commit install` as a manual step for when all checks pass.

### 2. `bug-fixes`
Remaining bugs not yet fixed on HEAD:

1. `pifs/base_pif.py:83` — `logging.warn()` → `logging.warning()`

### 3. `dead-code`
Remove all confirmed dead code:

- `pifs/noob-lottery.py` — entire file (hyphenated filename, not registered in `known_pif_types`)
- `utils/banner_helper.py` — no-op `banner_update()`, entire real implementation commented out
- `utils/subreddit_helper.py` — only called from banner_helper (dead), remove entire file
- `utils/imagery_helper.py` — only called from banner_helper (dead), remove entire file
- `utils/imgur_helper.py` — only called from subreddit_helper (dead), remove entire file
- `utils/file_system_helper.py` — only called from banner_helper/imagery_helper (dead), remove entire file
- `pifs/geo_pif.py:131-180` — remove commented-out plotly map rendering block
- `utils/pif_storage.py` — remove all commented-out cache code
- `utils/dynamo_helper.py:fetch_closed_pifs()` — defined but never called
- `utils/reddit_helper.py:submission_link(), comment_link()` — defined but never called
- `utils/karma_calculator.py:formatted_karma()` — remove unused `user` parameter

### 4. `configurable-subreddits`
Make monitored subreddits and karma scope configurable.

- Add to `config.py`:
  - `monitored_subreddits = "WetShaving+ircbst"` — multi-reddit string for streams
  - `karma_subreddit = "WetShaving"` — single subreddit for karma calculation
- `utils/reddit_helper.py` reads these from config instead of hardcoding:
  - `subreddit = reddit.subreddit(monitored_subreddits)`
  - `rwetshaving = reddit.subreddit(karma_subreddit)`
- All downstream consumers (`pifbot.py`, `karma_calculator.py`, CLI tools) use these variables unchanged — they just get configured values now.

### 5. `thread-safety`
Add `threading.Lock` around load-modify-save cycles.

- `utils/pif_storage.py`: wrap `save_pif`/`get_pif`/`get_open_pifs` in a module-level lock.
- All 5 daemon threads share the same storage facade — a single reentrant lock prevents two threads from loading the same PIF, modifying it, and clobbering each other.
- DynamoDB layer already handles its own concurrency; the local file backend already has per-instance locks. The facade lock ensures callers don't interleave load-modify-save across different PIFs.

### 6. `config-settings`
Migrate from bare `config.py` to `pydantic-settings BaseSettings`.

- Define `Settings(BaseSettings)` with all current config keys plus `monitored_subreddits` and `karma_subreddit`.
- Support `.env` file and environment variable override.
- `config.py` stays as a thin re-export or is replaced entirely.
- This is the last structural change before type annotations begin.

### 7. `types-utils`
Add full type annotations to all files under `utils/`:

- `utils/reddit_helper.py`, `utils/pif_storage.py`, `utils/dynamo_db_storage.py`, `utils/local_file_storage.py`, `utils/storage_protocol.py`, `utils/poker_util.py`, `utils/karma_calculator.py`, `utils/personality.py`
- Use `X | None`, `TypedDict` for DynamoDB dict shapes, `Protocol` where appropriate.
- Fix mypy errors in these files; remove from mypy exclusion list.

### 8. `types-pifs`
Add full type annotations to all files under `pifs/`:

- All game types, `pif_builder.py`, `base_pif.py`.
- Define `PifState`, `PifType`, etc. as `StrEnum` or `Literal` types.
- Fix mypy errors; remove from exclusion list.

### 9. `types-handlers`
Add full type annotations to `handlers/`:

- `comment_handler.py`, `submission_handler.py`, `periodic_check_handler.py`, `private_message_handler.py`
- Fix mypy errors; remove from exclusion list.

### 10. `pydantic-models`
Add Pydantic BaseModel for PIF domain objects.

- `PifModel(BaseModel)` with validated fields replacing raw dict construction.
- TypedDict for DynamoDB/LocalFile storage shapes.
- Migrate `build_from_ddb_dict` → `PifModel.model_validate()`.
- This is the deepest change — touches `pif_builder.py`, `base_pif.py`, both storage backends, and the facade.

### 11. `tests-core`
Set up pytest and test infrastructure.

- `conftest.py` with fixtures for storage backends (tmp_path), mock Reddit objects.
- Tests for `utils/poker_util.py` — pure logic, straightforward.
- Tests for both storage backends (save/get/exists round-trips).
- No mocking of DynamoDB — use the local file backend for tests.

### 12. `tests-pifs`
End-to-end tests for one PIF type (Lottery — simplest).

- Parse a mock Reddit post, enter mock users, finalize, verify winner.
- Tests for karma check logic.
- This completes the modernization.

## Risk & Rollback

Each branch is independently mergeable. If branch 10 (Pydantic models) causes a production regression, branches 1-9 are already deployed and safe. Rollback of any single branch is a `git revert` of its merge commit.
