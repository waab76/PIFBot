# Configurable Subreddits Implementation Plan

**Goal:** Make monitored subreddits and karma scope configurable via `config.py` instead of hardcoded in `reddit_helper.py`. Karma_subreddit becomes a list supporting multiple subreddits.

**Architecture:** New config values feed into `reddit_helper.py`. `rwetshaving` splits into `rwetshaving_ids` (set for quick membership checks) and `rwetshaving_label` (joined display name for templates). All downstream consumers update their imports accordingly.

**Tech Stack:** Pure config change, no new dependencies.

---

## File Map

| Action | File | Purpose |
|---|---|---|
| Modify | `config.py` | Replace `karma_subreddit` with `karma_subreddits` (list), add `monitored_subreddits` |
| Modify | `utils/reddit_helper.py` | Read from config, export `rwetshaving_ids` (set) + `rwetshaving_label` (string) |
| Modify | `utils/karma_calculator.py` | Use `rwetshaving_ids` for filtering, `rwetshaving_label` for display |

---

### Task 1: Add config values

**Files:**
- Modify: `config.py`

- [ ] **Step 1: Add `monitored_subreddits` and `karma_subreddits` to `config.py`**

Add after `log_path`:
```python
monitored_subreddits = "WetShaving+ircbst"
karma_subreddits = ["WetShaving"]
```

Note: `monitored_subreddits` is a single string (Reddit multi-reddit syntax uses `+` joiner). `karma_subreddits` is a list — each entry is checked independently when filtering comments/submissions for karma.

- [ ] **Step 2: Verify syntax**

```bash
python3 -m py_compile config.py
```

- [ ] **Checkpoint — user commits with message `chore: add subreddit config values`**

---

### Task 2: Update `utils/reddit_helper.py`

**Files:**
- Modify: `utils/reddit_helper.py`

- [ ] **Step 1: Replace hardcoded subreddit strings with config values**

Change lines 34-36 from:
```python
# Get a handle on our preferred subreddit
subreddit = reddit.subreddit("WetShaving+ircbst")
rwetshaving = reddit.subreddit("WetShaving")
```

To:
```python
from config import karma_subreddits, monitored_subreddits

# Get a handle on our preferred subreddit
subreddit = reddit.subreddit(monitored_subreddits)

# Build karma subreddit lookup set and display label
rwetshaving_objects = [reddit.subreddit(s) for s in karma_subreddits]
rwetshaving_ids = {s.id for s in rwetshaving_objects}
rwetshaving_label = ", ".join(karma_subreddits)
```

- `rwetshaving_ids` — a `set[str]` for O(1) subreddit membership checks (used by karma_calculator)
- `rwetshaving_label` — a comma-joined string like `"WetShaving"` or `"WetShaving, SomeOther"` for display

- [ ] **Step 2: Verify syntax**

```bash
python3 -m py_compile utils/reddit_helper.py
```

- [ ] **Checkpoint — user commits with message `feat: read subreddits from config, export ids set and label`**

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
from utils.reddit_helper import rwetshaving_ids, rwetshaving_label
```

- [ ] **Step 2: Update subreddit filtering (lines 88, 104)**

Change both:
```python
submission.subreddit_id[3:] == rwetshaving.id
comment.subreddit_id[3:] == rwetshaving.id
```
To:
```python
submission.subreddit_id[3:] in rwetshaving_ids
comment.subreddit_id[3:] in rwetshaving_ids
```

- [ ] **Step 3: Update template display names (lines 124-146)**

In `formatted_karma()`, replace all three occurrences of `rwetshaving.display_name` with `rwetshaving_label`.

Line 131:
```python
response = good_karma_template.format(
    rwetshaving_label, user.name, activity[1], activity[2], activity[0]
)
```

Line 135-143:
```python
    response = bad_karma_template.format(
        rwetshaving_label,
        user.name,
        ...
    )
```

Line 145-147:
```python
    response = new_karma_template.format(
        rwetshaving_label, user.name, activity[1], activity[2], activity[0]
    )
```

The templates already use `/r/{} overview for /u/{}` so with a single subreddit the output is `/r/WetShaving overview...` and with multiple it becomes `/r/WetShaving, SomeOther overview...` — both read naturally.

- [ ] **Step 4: Verify syntax**

```bash
python3 -m py_compile utils/karma_calculator.py
```

- [ ] **Checkpoint — user commits with message `feat: support multiple karma subreddits`**

---

### Verification

- [ ] **Final checklist**

- All 3 files compile
- `config.py` has `monitored_subreddits` (string) and `karma_subreddits` (list) with defaults matching old behavior
- `reddit_helper.py` exports `rwetshaving_ids` (set) and `rwetshaving_label` (string)
- `karma_calculator.py` uses `in rwetshaving_ids` for filtering and `rwetshaving_label` for display
- Downstream consumers of `subreddit` and `reddit` (15 import sites) need no changes
- No remaining references to the old `rwetshaving` symbol
