# Config Settings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate from bare module-level constants in `config.py` to `pydantic-settings BaseSettings`.

**Architecture:** Define a `Settings(BaseSettings)` class with all config values, instantiate once at module level, then re-export every value as a module-level name so all existing `from config import ...` imports continue to work unchanged.

**Tech Stack:** pydantic-settings, `.env` file, optional env var override

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `config.py` | Modify | Define `Settings` class, instantiate, re-export |
| `pyproject.toml` | Modify | Add pydantic-settings dependency, remove `config` from mypy ignore list |
| `.env.example` | Create | Document all config keys with placeholder values |
| `.pre-commit-config.yaml` | Modify | Track `.env.example` |
| `AGENTS.md` | Modify | Document new config mechanism |

No other files change — all existing `from config import ...` call sites work via the module-level re-exports.

---

### Task 1: Add pydantic-settings dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add pydantic-settings**

Run: `uv add pydantic-settings`

Expected: package added to `[project] dependencies` in `pyproject.toml`

- [ ] **Step 2: Commit**

---

### Task 2: Rewrite config.py with Settings class and re-exports

**Files:**
- Modify: `config.py`

- [ ] **Step 1: Write the Settings class and re-exports**

Replace entire `config.py` with:

```python
from typing import Dict, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PIFBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    blacklist: Dict[str, str] = {
        "BourbonExile": "This is just a test.",
        "MadShaver": "Selling PIF winnings is frowned upon.",
    }
    imgur_client_id: str = "803d6bf22fe330c"
    imgur_client_secret: str = "8d5e26716418b21cb26f827500d87aad2749c04c"
    log_path: str = "/home/pi/LatherBot.log"
    monitored_subreddits: List[str] = ["WetShaving", "ircbst"]
    karma_subreddits: List[str] = ["WetShaving"]
    storage_backend: str = "local"
    storage_path: str = "/tmp/pifbot_storage/pifs.json"


settings = Settings()

blacklist = settings.blacklist
imgur_client_id = settings.imgur_client_id
imgur_client_secret = settings.imgur_client_secret
log_path = settings.log_path
monitored_subreddits = settings.monitored_subreddits
karma_subreddits = settings.karma_subreddits
storage_backend = settings.storage_backend
storage_path = settings.storage_path
```

- [ ] **Step 2: Verify all 5 import sites still compile**

Run:
```bash
for f in utils/pif_storage.py utils/reddit_helper.py pifbot.py pifs/base_pif.py gen_map.py; do
    python3 -m py_compile "$f" && echo "$f PASS" || echo "$f FAIL"
done
```

Expected: all PASS

- [ ] **Step 3: Commit**

---

### Task 3: Remove config from mypy ignore list

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove `"config"` from the mypy overrides ignore list**

Edit `pyproject.toml` — remove the `"config",` line from the `[[tool.mypy.overrides]]` `module` list.

- [ ] **Step 2: Run mypy on config.py to verify it passes**

Run: `uv run mypy config.py`

Expected: Success (no issues found). If pydantic-settings generates complex types that mypy rejects, add a targeted `# type: ignore[assignment]` on the module-level re-exports.

- [ ] **Step 3: Commit**

---

### Task 4: Create .env.example

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Write .env.example**

```env
PIFBOT_BLACKLIST={"BourbonExile": "This is just a test."}
PIFBOT_IMGUR_CLIENT_ID=803d6bf22fe330c
PIFBOT_IMGUR_CLIENT_SECRET=8d5e26716418b21cb26f827500d87aad2749c04c
PIFBOT_LOG_PATH=/home/pi/LatherBot.log
PIFBOT_MONITORED_SUBREDDITS=["WetShaving", "ircbst"]
PIFBOT_KARMA_SUBREDDITS=["WetShaving"]
PIFBOT_STORAGE_BACKEND=local
PIFBOT_STORAGE_PATH=/tmp/pifbot_storage/pifs.json
```

- [ ] **Step 2: Verify .env.example is valid**

Run: `python3 -c "from pydantic_settings import BaseSettings; exec(open('config.py').read())"` — quick smoke check. Or just verify `uv run python3 -c "from config import settings; print(settings.model_dump())"` prints the expected defaults.

- [ ] **Step 3: Commit**

---

### Task 5: Update .pre-commit-config.yaml and AGENTS.md

**Files:**
- Modify: `pre-commit-config.yaml` (no change needed if `end-of-file-fixer` already tracks all files)
- Modify: `AGENTS.md`

- [ ] **Step 1: Add .env.example to pre-commit tracking if needed**

Check `.pre-commit-config.yaml` — if `end-of-file-fixer` and `trailing-whitespace` have no `files:` restriction, they already cover `.env.example`. No change needed.

- [ ] **Step 2: Update AGENTS.md**

Update the "Config" line under Startup & dependencies:

```markdown
- **Config**: `config.py` (gitignored) uses `pydantic-settings BaseSettings`. Configured via `.env` file or `PIFBOT_*` environment variables. See `.env.example` for all keys.
```

- [ ] **Step 3: Commit**

---

### Task 6: Final verification

- [ ] **Step 1: Run ruff**

```bash
uv run pre-commit run --all-files
```

Expected: all hooks pass

- [ ] **Step 2: Verify imports still work end-to-end**

```bash
uv run python3 -c "
from config import (
    blacklist, imgur_client_id, imgur_client_secret,
    log_path, monitored_subreddits, karma_subreddits,
    storage_backend, storage_path,
)
print('log_path:', log_path)
print('monitored_subreddits:', monitored_subreddits)
print('storage_backend:', storage_backend)
print('imgur_client_secret length:', len(imgur_client_secret))
"
```

Expected: prints correct values

- [ ] **Step 3: Present for review and commit**
