# Types — Utils Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add full type annotations to all 4 files under `utils/` and remove them from the mypy ignore list.

**Architecture:** One task per file, easiest first (pure logic → PRAW-dependent). Each file is annotated independently and verified with mypy strict mode. PRAW types use `# type: ignore[import-untyped]` since praw lacks official stubs.

**Tech Stack:** mypy strict mode, Python 3.11 type syntax (`X | None`, `list[X]`)

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `utils/poker_util.py` | Modify | Add type annotations for all 12 functions + module-level constants |
| `utils/personality.py` | Modify | Add type annotations for bad_command_responses list + function |
| `utils/karma_calculator.py` | Modify | Add type annotations, template strings, tuple return types |
| `utils/reddit_helper.py` | Modify | Add type annotations for module-level PRAW objects + 3 functions |
| `pyproject.toml` | Modify | Remove 4 utils modules from mypy ignore; remove dead `utils.dynamo_helper` entry |

---

### Task 1: Annotate poker_util.py

**Files:**
- Modify: `utils/poker_util.py`

**Notes:** Pure logic — no PRAW, no external dependencies. A `Card = tuple[int | str, str]` type alias simplifies all function signatures. Functions like `is_straight`, `is_flush`, `hand_score` are deterministic and easy to annotate.

- [ ] **Step 1: Add from __future__ import and type alias**

Add `from __future__ import annotations` after the license block, before `import logging`. Then add the type alias after the imports:

```python
from __future__ import annotations

import logging
import random

Card = tuple[int | str, str]
```

Add a `Card` type alias after the imports:
```python
Card = tuple[int | str, str]
```

- [ ] **Step 2: Add type annotations to all functions**

| Function | Signature |
|---|---|
| `new_deck()` | `def new_deck() -> list[Card]` |
| `deal_card(deck)` | `def deal_card(deck: list[Card]) -> Card` |
| `card_name(card)` | `def card_name(card: Card) -> str` |
| `card_point_value(card)` | `def card_point_value(card: Card) -> int` |
| `format_card(card)` | `def format_card(card: Card) -> str` |
| `order_cards(hand)` | `def order_cards(hand: list[Card]) -> list[Card]` |
| `ordered_hand_values(ordered_hand)` | `def ordered_hand_values(ordered_hand: list[Card]) -> str` |
| `is_straight(hand)` | `def is_straight(hand: list[Card]) -> bool` |
| `is_flush(hand)` | `def is_flush(hand: list[Card]) -> bool` |
| `check_multiples(hand)` | `def check_multiples(hand: list[Card]) -> list[list]` |
| `compute_dup_values(hand)` | `def compute_dup_values(hand: list[Card]) -> str | bool` |
| `determine_hand(hand)` | `def determine_hand(hand: list[Card]) -> str` |
| `determine_high_card(hand)` | `def determine_high_card(hand: list[Card]) -> str` |
| `hand_score(hand)` | `def hand_score(hand: list[Card]) -> int` |

- [ ] **Step 3: Verify compilation**

Run: `uv run python3 -m py_compile utils/poker_util.py`

Expected: PASS

- [ ] **Step 4: Run mypy**

Run: `uv run mypy utils/poker_util.py`

Expected: Success — no issues found. If errors occur, add necessary annotations or `# type: ignore` comments.

---

### Task 2: Annotate personality.py

**Files:**
- Modify: `utils/personality.py`

**Notes:** Trivial file — one list of strings and one function.

- [ ] **Step 1: Add `from __future__ import annotations` and type annotations**

Add `from __future__ import annotations` after the license block, before `import random`. Then annotate:

```python
from __future__ import annotations

import random


bad_command_responses: list[str] = [
    "My dude, I don't understand what you're trying to do.",
    ...
]


def get_bad_command_response() -> str:
    return random.choice(bad_command_responses)
```

- [ ] **Step 2: Verify compilation and mypy**

Run:
```bash
uv run python3 -m py_compile utils/personality.py
uv run mypy utils/personality.py
```

Expected: both PASS

---

### Task 3: Annotate karma_calculator.py

**Files:**
- Modify: `utils/karma_calculator.py`

**Notes:** Uses PRAW `user` objects. `calculate_karma` returns a 5-tuple. `formatted_karma` takes a user and a 5-tuple. `formatted_karma_check` is a convenience wrapper. Template strings are module-level constants.

The PRAW `Redditor` type has no stubs — use `from praw.models import Redditor` if available, or `typing.Any` for the user parameter.

`calculate_karma` return type: `tuple[int, int, int, int, int]` (karma, submissions, comments, pif_comment_karma, pif_comments). This is a `KarmaResult` type alias.

- [ ] **Step 1: Add type alias and annotations**

```python
from __future__ import annotations

import logging
import time

from praw.models import Redditor

from utils.reddit_helper import karma_subreddit_ids, karma_subreddit_label

KarmaResult = tuple[int, int, int, int, int]

good_karma_template: str = """
...
"""

bad_karma_template: str = """
...
"""

new_karma_template: str = """
...
"""


def calculate_karma(user: Redditor) -> KarmaResult:
    ...


def formatted_karma(user: Redditor, activity: KarmaResult) -> str:
    ...


def formatted_karma_check(user: Redditor) -> str:
    ...
```

If `praw.models.Redditor` is not importable (no stubs), use `from typing import Any` and annotate `user: Any` instead.

- [ ] **Step 2: Verify compilation and mypy**

Run:
```bash
uv run python3 -m py_compile utils/karma_calculator.py
uv run mypy utils/karma_calculator.py
```

Expected: both PASS. If mypy errors on `Redditor` import, switch to `Any`.

---

### Task 4: Annotate reddit_helper.py

**Files:**
- Modify: `utils/reddit_helper.py`

**Notes:** Module-level PRAW objects. `praw.Reddit` has no stubs. The `skip_comment` function takes a PRAW `Comment` object — use `from praw.models import Comment` (already imported). Add `from __future__ import annotations` after the license block.

`Subreddit` type: PRAW 7.x exports `Subreddit` from `praw.models`, but type stubs may be incomplete. If mypy cannot resolve the import, use `Any` from `typing` instead.

Approach:
- `reddit: praw.Reddit` — annotate with `# type: ignore[import-untyped]` on the `import praw` line if mypy complains
- `monitored_sub` — `Subreddit` if importable, else `Any`
- `karma_subreddit_ids` — `set[str]`
- `karma_subreddit_label` — `str`
- Function parameters and return types

- [ ] **Step 1: Add type annotations**

```python
from __future__ import annotations

import logging

import praw  # type: ignore[import-untyped]
from praw.models import Comment, Subreddit, Submission

from config import karma_subreddits, monitored_subreddits

bot_name: str = "PIFBot"
user_agent: str = "script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"

reddit: praw.Reddit = praw.Reddit(bot_name, user_agent=user_agent)

monitored_sub: Subreddit = reddit.subreddit("+".join(monitored_subreddits))

_karma_subs: list[Subreddit] = [reddit.subreddit(s) for s in karma_subreddits]
karma_subreddit_ids: set[str] = {s.id for s in _karma_subs}
karma_subreddit_label: str = ", ".join(f"/r/{s}" for s in karma_subreddits)


def get_submission(post_id: str) -> Submission:
    return Submission(reddit, post_id)


def get_comment(comment_id: str) -> Comment:
    return Comment(reddit, comment_id)


def skip_comment(comment: Comment) -> bool:
    ...
```

- [ ] **Step 2: Verify compilation and mypy**

Run:
```bash
uv run python3 -m py_compile utils/reddit_helper.py
uv run mypy utils/reddit_helper.py
```

Expected: both PASS. If mypy errors on `Subreddit` type (praw may not export it), use `Any` and import from `typing`.

---

### Task 5: Update pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove annotated modules from mypy ignore list**

From `pyproject.toml` `[[tool.mypy.overrides]]` `module` list, remove:
- `"utils.reddit_helper",`
- `"utils.poker_util",`
- `"utils.karma_calculator",`
- `"utils.personality",`

Also remove the dead entry:
- `"utils.dynamo_helper",` — this file has been deleted, nothing references it

Final list:
```toml
module = [
    "handlers.*",
    "pifbot",
    "check_comment",
    "finalize",
    "karma",
    "pif_stats",
    "poker",
]
```

- [ ] **Step 2: Run mypy on all 4 annotated utils files**

Run:
```bash
uv run mypy utils/poker_util.py utils/personality.py utils/karma_calculator.py utils/reddit_helper.py
```

Expected: Success — no issues found in 4 source files

- [ ] **Step 3: Run ruff on utils/**

Run: `uv run ruff check utils/`

Expected: all checks pass (or only pre-existing E501 line-length issues)

---

### Task 6: Final smoke test

- [ ] **Step 1: Verify all utils files import correctly**

Run:
```bash
uv run python3 -c "
from utils.poker_util import new_deck, deal_card, hand_score, determine_hand
from utils.personality import get_bad_command_response
from utils.reddit_helper import get_submission, get_comment, skip_comment, reddit, monitored_sub
print('poker_util:', new_deck()[:2])
print('personality:', get_bad_command_response())
print('reddit_helper:', type(reddit).__name__, type(monitored_sub).__name__)
"
```

Expected: prints without error. Note: `karma_calculator` is not imported here because it requires Reddit API access to actually call `calculate_karma`.
