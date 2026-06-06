# Entrypoints + Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Annotate the 6 remaining entrypoint files and clean up stale `type: ignore` comments, then remove the last `ignore_errors` block from pyproject.toml.

**Architecture:** `pifbot.py` is the main daemon (spawns 5 threads, imports everything). `pif_stats.py` accesses `fetch_all_pifs()` which now returns `list[BasePIF]` instead of raw dicts — needs dict→attribute access refactor. The remaining 4 CLI scripts (`poker.py`, `karma.py`, `finalize.py`, `check_comment.py`) are tiny (15-45 lines each).

**Tech Stack:** Python 3.11 strict mypy, PRAW 7.x (no stubs, use `# type: ignore[import-untyped]`), `BasePIF` typed via pydantic-models + pif-subclasses branches.

---

### Task 0: Clean up unused type:ignore in base_pif.py

**Files:**
- Modify: `pifs/base_pif.py`

5 stale `# type: ignore[no-untyped-call]` comments linger from the pydantic-models branch. They're on lines where `get_submission()` and `calculate_karma()` are called — these functions are now typed, so the ignores are unused and flagged by `mypy --strict`.

- [ ] **Step 1: Remove the 5 unused type:ignore comments**

The comments are on these lines (from pydantic-models branch):

```
line 59: get_submission(self.postId)  # type: ignore[no-untyped-call]
line 77: calculate_karma(user)  # type: ignore[no-untyped-call]
line 84: formatted_karma(user, karma)  # type: ignore[no-untyped-call]
line 172: comment.reply(...)  # type: ignore[no-untyped-call]
line 197: submission.reply(...)  # type: ignore[no-untyped-call]
```

Remove each `  # type: ignore[no-untyped-call]` suffix. The exact line numbers may have shifted from the ABC refactor — search for `# type: ignore[no-untyped-call]` in the file and remove all 5 occurrences.

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy pifs/base_pif.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 1: Refactor and annotate pif_stats.py

**Files:**
- Modify: `pif_stats.py`

`fetch_all_pifs()` now returns `list[BasePIF]` instead of raw dicts. The file accesses `pif["SubmissionId"]`, `pif["PifType"]`, etc. These need to become `pif.postId`, `pif.pifType`, etc. Also needs `from __future__ import annotations` and type annotations.

- [ ] **Step 1: Rewrite dict access to attribute access + add annotations**

Current file structure (116 lines). Here's the mapping of dict keys to BasePIF attributes:

| Dict key | BasePIF attribute |
|---|---|
| `pif["SubmissionId"]` | `pif.postId` |
| `pif["PifType"]` | `pif.pifType` |
| `pif["Author"]` | `pif.authorName` |
| `pif["PifWinner"]` | `pif.pifWinner` |
| `pif["PifEntries"]` | `pif.pifEntries` |

The file currently runs its logic at module level (no function wrapper). It should be wrapped in a `main()` function so types flow properly.

Replace the entire file with:

```python
from __future__ import annotations

import time
from typing import Any

from pifs import pif_builder
from utils import poker_util, reddit_helper
from utils.pif_storage import fetch_all_pifs


def main() -> None:
    pif_list = fetch_all_pifs()
    piffers: dict[str, int] = {}
    winners: dict[str, int] = {}
    pif_types: dict[str, int] = {}
    pif_type_entries: dict[str, int] = {}
    entrants: dict[str, int] = {}
    pif_count = 0
    entry_count = 0
    history_days = 180
    thirty_days_ago = time.time() - (history_days * 24 * 60 * 60)
    best_poker_hand_score = 0
    best_poker_hand_user = "TBD"
    best_poker_hand: list[Any] = []

    for pif_type in pif_builder.known_pif_types:
        pif_types[pif_type] = 0
        pif_type_entries[pif_type] = 0

    for pif in pif_list:
        submission = reddit_helper.reddit.submission(pif.postId)
        if submission.created_utc < thirty_days_ago:
            continue

        pif_type = pif.pifType
        pif_count += 1

        if pif.authorName not in piffers:
            piffers[pif.authorName] = 0
        piffers[pif.authorName] += 1

        if pif.pifWinner != "TBD":
            if pif.pifWinner not in winners:
                winners[pif.pifWinner] = 0
            winners[pif.pifWinner] += 1

            if pif_type == "infinite-poker":
                if pif.pifEntries[pif.pifWinner]["HandScore"] > best_poker_hand_score:
                    best_poker_hand_score = pif.pifEntries[pif.pifWinner]["HandScore"]
                    best_poker_hand_user = pif.pifWinner
                    best_poker_hand = pif.pifEntries[pif.pifWinner]["UserHand"]

        pif_types[pif_type] += 1

        for entrant in pif.pifEntries:
            if entrant not in entrants:
                entrants[entrant] = 0
            entrants[entrant] += 1
            entry_count += 1
            pif_type_entries[pif_type] += 1

    sorted_piffers = sorted(piffers.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_pif_types = sorted(pif_types.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_winners = sorted(winners.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    sorted_entrants = sorted(entrants.items(), key=lambda kv: (kv[1], kv[0]))[::-1]

    print(f"""
LatherBot PIF stats for the trailing {history_days} days

\--------------------------------------------

{pif_count} PIFs by {len(piffers)} Redditors:

|Redditor|PIFs|
|:-|:-|""")

    for piffer in sorted_piffers:
        print(f"|u/{piffer[0]}|{piffer[1]}|")

    print(f"""\nThere were {entry_count} entries across the {pif_count} PIFs. The top 10 most active PIF contestants were:

|Redditor|Entries|
|:-|:-|""")
    for i in range(10):
        print(f"|u/{sorted_entrants[i][0]}|{sorted_entrants[i][1]}|")

    print("\nWinningest Redditors:\n\n|Redditor|Wins|\n|:-|:-|")
    for pif_winner in sorted_winners:
        print(f"|u/{pif_winner[0]}|{pif_winner[1]}|")

    print("\nMost popular PIF types:\n\n|PIF Type|Count|Entries per PIF|\n|:-|:-|:-|")
    for pif_type in sorted_pif_types:
        avg_entries: float = 0
        if pif_type[1] > 0:
            avg_entries = round(pif_type_entries[pif_type[0]] / pif_type[1], 2)
        print(f"|{pif_type[0]}|{pif_type[1]}|{avg_entries}|")

    print(
        f"\nBest poker hand: {best_poker_hand_user} with {poker_util.determine_hand(best_poker_hand)}"
    )


if __name__ == "__main__":
    main()
```

Key changes from current file:
1. Add `from __future__ import annotations` at top
2. Add `from typing import Any` for `best_poker_hand`
3. Wrap module-level code in `main() -> None`
4. All dict-style accesses (`pif["SubmissionId"]`) → attribute access (`pif.postId`)
5. `for entrant in pif["PifEntries"].keys():` → `for entrant in pif.pifEntries:`
6. Add `: dict[str, int]` annotations to accumulator dicts, `: list[Any]` to `best_poker_hand`
7. `avg_entries: float = 0` annotation

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy pif_stats.py
```

Expected: Success — no issues found. If `reddit_helper.reddit` type causes issues, add `# type: ignore[import-untyped]` or `# type: ignore[no-untyped-call]` as needed.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 2: Annotate poker.py

**Files:**
- Modify: `poker.py`

Tiny test file (102 lines). Pure poker_util calls, no PRAW dependencies.

- [ ] **Step 1: Add from __future__ import annotations and type annotations**

Add `from __future__ import annotations` after the license block (line 19 blank). Then annotate:

- `hands: list[list[Any]] = []` — or `list[Card]` but Card is in poker_util, so `list[list[Any]]` is simpler
- `tied_winners: list[list[Any]] = []`
- `shared_cards: list[list[Any]] = []`
- `hand: list[list[Any]] = []`
- `deck: list[Card]` — wait, `Card` is `list[int | str]` and is imported via `poker_util`. Use `from utils.poker_util import Card` or just annotate as `list[list[int | str]]` or `list[Any]`.

Simplest approach that avoids cross-module import complexity:
```python
from __future__ import annotations

from typing import Any

from utils import poker_util


def test_hands() -> None:
    hands: list[list[Any]] = []
    ...
    for hand in hands:
        print(f"{hand} - {poker_util.determine_hand(hand)} - {poker_util.hand_score(hand)}")


def test_poker() -> None:
    deck: list[list[Any]] = poker_util.new_deck()
    tied_winners: list[list[Any]] = []
    curr_max_score = 0
    shared_cards: list[list[Any]] = []
    ...
```

The `list[list[Any]]` type is loose but accurate — poker_util's `Card` type is `list[int | str]`, and `Any` is the simplest way to represent the unpacked card lists from the function output.

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy poker.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 3: Annotate karma.py

**Files:**
- Modify: `karma.py`

Tiny CLI (24 lines). Creates a PRAW Reddit instance and calls `formatted_karma_check`.

- [ ] **Step 1: Add from __future__ import annotations and type annotations**

```python
from __future__ import annotations

import sys

import praw  # type: ignore[import-untyped]

from utils.karma_calculator import formatted_karma_check


bot_name: str = "PIFBot"
user_agent: str = "script:PIFBot:0.1 (by u/BourbonInExile and u/MrSabuhudo)"


def check_karma() -> None:
    reddit: praw.Reddit = praw.Reddit(bot_name, user_agent=user_agent)
    user = reddit.redditor(sys.argv[1])
    print(formatted_karma_check(user))


if __name__ == "__main__":
    check_karma()
```

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy karma.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 4: Annotate finalize.py

**Files:**
- Modify: `finalize.py`

Tiniest CLI (18 lines). Simple function call.

- [ ] **Step 1: Add from __future__ import annotations and type annotations**

```python
from __future__ import annotations

import sys

from pifs.base_pif import BasePIF
from utils.pif_storage import get_pif


def finalize(pif_id: str) -> None:
    pif: BasePIF | None = get_pif(pif_id)
    if pif is not None:
        pif.finalize()


if __name__ == "__main__":
    finalize(sys.argv[1])
```

Note: `get_pif` now returns `BasePIF | None` (from the handlers branch). The original code silently passed `None` to `.finalize()` which would crash. Added the `is not None` guard.

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy finalize.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 5: Annotate check_comment.py

**Files:**
- Modify: `check_comment.py`

Small CLI (45 lines). Fetches a comment and delegates to comment_handler.

- [ ] **Step 1: Add from __future__ import annotations and type annotations**

```python
from __future__ import annotations

import sys

from praw.models import Comment  # type: ignore[import-untyped]

from handlers import comment_handler
from utils import reddit_helper


def main() -> None:
    for arg in sys.argv[1:]:
        print(arg)


def check_comment(comment_id: str) -> None:
    comment: Comment = reddit_helper.reddit.comment(id=comment_id)

    print(f"got comment [{comment.body}]")

    for line in comment.body.lower().split("\n"):
        print(line.split())

    comment_handler.handle_comment(comment)


if __name__ == "__main__":
    check_comment(sys.argv[1])
```

Key changes:
1. Add `from __future__ import annotations` after license block
2. Import `Comment` from `praw.models`
3. `main() -> None` annotation
4. `check_comment(comment_id: str) -> None`
5. `comment: Comment` local annotation
6. Remove the inline comment `# print command line arguments`

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy check_comment.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 6: Annotate pifbot.py

**Files:**
- Modify: `pifbot.py`

The main daemon (144 lines). Spawns 5 threads. Has complex PRAW imports (`from praw.models.reddit import comment, submission` — these are modules, not classes).

- [ ] **Step 1: Add from __future__ import annotations and type annotations**

```python
from __future__ import annotations

import datetime
import logging
import sys
import threading
import time
from logging.handlers import TimedRotatingFileHandler

from config import log_path

handlers: list[TimedRotatingFileHandler] = [
    TimedRotatingFileHandler(log_path, when="W3", interval=1, backupCount=4)
]

logging.basicConfig(
    level=logging.INFO,
    handlers=handlers,
    format="%(asctime)s %(levelname)s %(threadName)s %(module)s:%(funcName)s %(message)s ",
)
logging.Formatter.formatTime = lambda self, record, datefmt=None: (
    datetime.datetime.fromtimestamp(record.created, datetime.UTC)
    .astimezone()
    .isoformat(sep="T", timespec="milliseconds")
)

from praw.models import Comment, Submission  # type: ignore[import-untyped]
from praw.models.util import stream_generator
from prawcore import ServerError

from handlers.comment_handler import handle_comment
from handlers.periodic_check_handler import check_and_update_pifs
from handlers.private_message_handler import handle_private_message
from handlers.submission_handler import handle_submission
from utils.reddit_helper import monitored_sub, reddit

logging.info("Connected to Reddit instance as %s", reddit.user.me())


def monitor_submissions() -> None:
    logging.info("Monitoring submissions for r/%s", monitored_sub.display_name)
    while True:
        submission_stream = monitored_sub.stream.submissions()
        try:
            for submission in submission_stream:
                handle_submission(submission)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error(
                "Error processing submission: %s", sys.exc_info()[0], exc_info=True
            )


def monitor_comments() -> None:
    while True:
        logging.info("Monitoring comments for r/%s", monitored_sub.display_name)
        comment_stream = monitored_sub.stream.comments()
        try:
            for comment in comment_stream:
                handle_comment(comment)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error(
                "Error processing comment: %s", sys.exc_info()[0], exc_info=True
            )


def monitor_edits() -> None:
    while True:
        logging.info("Monitoring r/%s edits", monitored_sub.display_name)
        edited_stream = stream_generator(monitored_sub.mod.edited, pause_after=0)
        try:
            for item in edited_stream:
                if isinstance(item, Comment):
                    logging.info(
                        'Comment [%s] on submission "%s" was edited by %s',
                        item.id,
                        item.submission.title,
                        item.author.name,
                    )
                    handle_comment(item)
                elif isinstance(item, Submission):
                    logging.info(
                        'Submission "%s" was edited by %s', item.title, item.author.name
                    )
                    handle_submission(item)
                elif item is not None:
                    logging.error("Unknown edited item type: %s", type(item))
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


def monitor_private_messages() -> None:
    while True:
        logging.info("Monitoring inbox")
        inbox_stream = reddit.inbox.stream(pause_after=-1)
        try:
            for inbox_item in reddit.inbox.stream():
                if hasattr(inbox_item, "name") and str(inbox_item.name).startswith("t4"):
                    handle_private_message(inbox_item)
        except ServerError:
            logging.error("Reddit server is down: %s", sys.exc_info()[0], exc_info=True)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


def periodic_pif_updates() -> None:
    while True:
        logging.info("Beginning periodic PIF update thread")
        try:
            while True:
                check_and_update_pifs()
                time.sleep(600)
        except Exception:
            logging.error("Caught exception: %s", sys.exc_info()[0], exc_info=True)


logging.debug("Starting child threads")
threading.Thread(target=periodic_pif_updates, name="updater").start()
threading.Thread(target=monitor_submissions, name="submissions").start()
threading.Thread(target=monitor_comments, name="comments").start()
threading.Thread(target=monitor_edits, name="edits").start()
threading.Thread(target=monitor_private_messages, name="pms").start()
```

Key changes from current file:
1. Add `from __future__ import annotations` at top (after license block, before `import datetime`)
2. Replace `from praw.models.reddit import comment, submission` with `from praw.models import Comment, Submission` — use the actual classes instead of module-level imports. This is needed for `isinstance` checks in `monitor_edits` and avoids the module import pattern.
3. `handlers: list[TimedRotatingFileHandler] = [...]`
4. All 5 functions: `-> None` return type
5. `monitor_private_messages`: change `inbox_item.name.startswith("t4")` to a safer `hasattr(inbox_item, "name") and str(inbox_item.name).startswith("t4")` since the PRAW stream might yield items without `name`.
6. Remove the `# TODO` comment about documentation reference

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy pifbot.py
```

Expected: Success — no issues found. May need `# type: ignore[import-untyped]` on `from praw.models.util import stream_generator` if that import causes issues.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 7: Update pyproject.toml and full smoke test

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove the last ignore_errors block**

Current state (after previous removals):
```toml
[[tool.mypy.overrides]]
module = [
    "pifbot",
    "check_comment",
    "finalize",
    "karma",
    "pif_stats",
    "poker",
]
ignore_errors = true
```

Delete the entire block. If this is the last override, the `[[tool.mypy.overrides]]` section header disappears too (no modules left to override).

- [ ] **Step 2: Verify all entrypoints pass mypy**

```bash
uv run mypy pifbot.py check_comment.py finalize.py karma.py pif_stats.py poker.py
```

Expected: Success — no issues found in 6 source files.

- [ ] **Step 3: Full project smoke test**

```bash
uv run mypy .
```

Expected: Success — no issues found.

- [ ] **Step 4: Commit** — SKIP THIS. Do NOT commit.
