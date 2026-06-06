# Configurable Subreddits Implementation Plan

**Goal:** Make monitored subreddits and karma scope configurable via `config.py`. Rename `subreddit` → `monitored_sub` and replace `rwetshaving` with `karma_subreddit_ids` + `karma_subreddit_label`. Both config values become lists.

**Architecture:** New list-based config values feed into `reddit_helper.py`. The monitored subreddits list is joined with `+` for PRAW's multi-reddit syntax. The karma subreddits list produces a set of IDs for filtering and a joined label for display. Four downstream files update their import names.

**Tech Stack:** Pure config change, no new dependencies.

---

## File Map

| Action | File | Purpose |
|---|---|---|
| Modify | `config.py` | Add `monitored_subreddits` (list), `karma_subreddits` (list) |
| Modify | `utils/reddit_helper.py` | Read config, rename exports |
| Modify | `utils/karma_calculator.py` | Use new names and set-based filtering |
| Modify | `pifbot.py` | Update `subreddit` → `monitored_sub` |
| Modify | `lgstats.py` | Update `subreddit` → `monitored_sub` |
| Modify | `roty.py` | Update `subreddit` → `monitored_sub` |
| Modify | `karma_roundup.py` | Update `subreddit` → `monitored_sub` |

---

### Task 1: Add config values

**Files:**
- Modify: `config.py`

- [ ] **Step 1: Add `monitored_subreddits` and `karma_subreddits` to `config.py`**

Add after `log_path`:
```python
monitored_subreddits = ["WetShaving", "ircbst"]
karma_subreddits = ["WetShaving"]
```

Both are lists. `monitored_subreddits` will be joined with `+` for PRAW's multi-reddit syntax internally. `karma_subreddits` produces a set of IDs for O(1) membership checks and a joined label for display.

- [ ] **Step 2: Verify syntax**

```bash
python3 -m py_compile config.py
```

- [ ] **Checkpoint — user commits with message `chore: add monitored_subreddits and karma_subreddits config values`**

---

### Task 2: Update `utils/reddit_helper.py`

**Files:**
- Modify: `utils/reddit_helper.py`

- [ ] **Step 1: Replace hardcoded subreddit strings and rename exports**

Replace the bottom of the file (lines 34-36) with config-driven initialization:

```python
from config import karma_subreddits, monitored_subreddits

# Build the monitored multi-reddit from the configured list
monitored_sub = reddit.subreddit("+".join(monitored_subreddits))

# Build karma subreddit lookup set and display label
_karma_subs = [reddit.subreddit(s) for s in karma_subreddits]
karma_subreddit_ids = {s.id for s in _karma_subs}
karma_subreddit_label = ", ".join(f"/r/{s}" for s in karma_subreddits)
```

Changes:
- `subreddit` → `monitored_sub` — PRAW multi-reddit object for streaming
- `rwetshaving` removed — replaced by:
  - `karma_subreddit_ids` — `set[str]` for O(1) subreddit membership checks
  - `karma_subreddit_label` — comma-joined string with `/r/` prefixes, like `"/r/WetShaving"` or `"/r/WetShaving, /r/SomeOther"`
- `monitored_subreddits` list is joined with `+` for multi-reddit syntax
- `_karma_subs` is private (leading underscore) — internal helper, not exported

- [ ] **Step 2: Verify syntax**

```bash
python3 -m py_compile utils/reddit_helper.py
```

- [ ] **Checkpoint — user commits reddit_helper.py changes**

---

### Task 3: Update `utils/karma_calculator.py`

**Files:**
- Modify: `utils/karma_calculator.py`

- [ ] **Step 1: Update imports**

Change line 24:
```python
from utils.reddit_helper import rwetshaving
```
To:
```python
from utils.reddit_helper import karma_subreddit_ids, karma_subreddit_label
```

- [ ] **Step 2: Update subreddit filtering (lines 88, 104)**

Change both:
```python
submission.subreddit_id[3:] == rwetshaving.id
comment.subreddit_id[3:] == rwetshaving.id
```
To:
```python
submission.subreddit_id[3:] in karma_subreddit_ids
comment.subreddit_id[3:] in karma_subreddit_ids
```

- [ ] **Step 3: Update template strings — remove `/r/` prefix from templates (now in the label)**

Change the three template strings (lines 27, 39, 53) from:
```python
/r/{} overview for /u/{} for the last 90 days:
```
To:
```python
{} overview for /u/{} for the last 90 days:
```

The `/r/` prefix is now baked into `karma_subreddit_label` itself (e.g., `"/r/WetShaving"` or `"/r/WetShaving, /r/SomeOther"`).

- [ ] **Step 4: Update template display names (lines 124-146)**

Replace all three occurrences of `rwetshaving.display_name` with `karma_subreddit_label`:

Line 131-133:
```python
    response = good_karma_template.format(
        karma_subreddit_label, user.name, activity[1], activity[2], activity[0]
    )
```

Lines 135-143:
```python
    if activity[3] > activity[0] / 3:
        response = bad_karma_template.format(
            karma_subreddit_label,
            user.name,
            activity[1],
            activity[2],
            activity[4],
            activity[0],
            activity[3],
        )
```

Lines 144-147:
```python
    elif activity[1] < 2 and activity[2] < 5:
        response = new_karma_template.format(
            karma_subreddit_label,
            user.name,
            activity[1],
            activity[2],
            activity[0],
        )
```

- [ ] **Step 5: Verify syntax**

```bash
python3 -m py_compile utils/karma_calculator.py
```

- [ ] **Checkpoint — user commits karma_calculator.py changes**

---

### Task 4: Update `pifbot.py`

**Files:**
- Modify: `pifbot.py`

- [ ] **Step 1: Update import**

Change line 51:
```python
from utils.reddit_helper import reddit, subreddit
```
To:
```python
from utils.reddit_helper import reddit, monitored_sub
```

- [ ] **Step 2: Update all references to `subreddit` → `monitored_sub`**

Six references in `pifbot.py`:

| Line | Current | New |
|---|---|---|
| 57 | `subreddit.display_name` | `monitored_sub.display_name` |
| 59 | `subreddit.stream.submissions()` | `monitored_sub.stream.submissions()` |
| 73 | `subreddit.display_name` | `monitored_sub.display_name` |
| 74 | `subreddit.stream.comments()` | `monitored_sub.stream.comments()` |
| 88 | `subreddit.display_name` | `monitored_sub.display_name` |
| 89 | `subreddit.mod.edited` | `monitored_sub.mod.edited` |

- [ ] **Step 3: Verify syntax**

```bash
python3 -m py_compile pifbot.py
```

- [ ] **Checkpoint — user commits pifbot.py changes**

---

### Task 5: Update `lgstats.py`

**Files:**
- Modify: `lgstats.py`

- [ ] **Step 1: Update import**

Change line 9:
```python
from utils.reddit_helper import subreddit
```
To:
```python
from utils.reddit_helper import monitored_sub
```

- [ ] **Step 2: Update reference**

Change line 13:
```python
posts = subreddit.search(...)
```
To:
```python
posts = monitored_sub.search(...)
```

- [ ] **Step 3: Verify syntax**

```bash
python3 -m py_compile lgstats.py
```

- [ ] **Checkpoint — user commits lgstats.py changes**

---

### Task 6: Update `roty.py`

**Files:**
- Modify: `roty.py`

- [ ] **Step 1: Update import**

Change line 7:
```python
from utils.reddit_helper import subreddit
```
To:
```python
from utils.reddit_helper import monitored_sub
```

- [ ] **Step 2: Update reference**

Change line 10:
```python
lg_sotds = subreddit.search(...)
```
To:
```python
lg_sotds = monitored_sub.search(...)
```

- [ ] **Step 3: Verify syntax**

```bash
python3 -m py_compile roty.py
```

- [ ] **Checkpoint — user commits roty.py changes**

---

### Task 7: Update `karma_roundup.py`

**Files:**
- Modify: `karma_roundup.py`

- [ ] **Step 1: Update import**

Change line 8:
```python
from utils.reddit_helper import reddit, subreddit
```
To:
```python
from utils.reddit_helper import reddit, monitored_sub
```

- [ ] **Step 2: Update reference**

Change line 14:
```python
sotd_posts = subreddit.search(...)
```
To:
```python
sotd_posts = monitored_sub.search(...)
```

- [ ] **Step 3: Verify syntax**

```bash
python3 -m py_compile karma_roundup.py
```

- [ ] **Checkpoint — user commits karma_roundup.py changes**

---

### Verification

- [ ] **Final checklist**

```bash
# No remaining references to old names in .py files
grep -rn "from utils.reddit_helper import.*subreddit\|from utils.reddit_helper import.*rwetshaving\|rwetshaving\.\|\.subreddit\b" --include="*.py" .
# Expected: no matches (false positives possible in docstrings/comments)

# All modified files compile
for f in utils/reddit_helper.py utils/karma_calculator.py pifbot.py lgstats.py roty.py karma_roundup.py; do
    python3 -m py_compile "$f" && echo "$f OK"
done
# Expected: all OK
```
