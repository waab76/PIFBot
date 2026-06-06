# PIF Subclasses Type Annotations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add strict mypy type annotations to all 9 PIF subclass files and remove them from the mypy ignore list.

**Architecture:** 9 PIF subclasses in `pifs/` extend `BasePIF` (which is already fully typed). Each subclass overrides a subset of methods (`__init__`, `pif_instructions`, `handle_entry`, `determine_winner`, `generate_winner_comment`, `is_already_entered`, `handle_comment`, `finalize`). Common types: `Comment` / `Redditor` from PRAW, `list[str]` for command_parts, `dict[str, Any]` for pifEntries/pifOptions.

**Tech Stack:** Python 3.11 strict mypy, PRAW 7.x (no stubs, use `# type: ignore[import-untyped]`), `poker_util` (typed via types-utils branch), `BasePIF` (typed via pydantic-models branch).

---

### Task 0: Add ABC to BasePIF

**Files:**
- Modify: `pifs/base_pif.py`
- Modify: `pifs/karma_only_pif.py`

Make `BasePIF` an abstract base class with 4 abstract methods. KarmaOnly implements them as explicit no-ops (documenting its outlier status). This gives compile-time enforcement that every "normal" PIF subclass implements the contract.

- [ ] **Step 1: Add ABC to base_pif.py**

Add import at line 21 and change class declaration:

```python
import logging
from abc import ABC, abstractmethod
from typing import Any

from config import blacklist
from pifs.models import PifStorageDict
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.personality import get_bad_command_response
from utils.reddit_helper import get_submission


class BasePIF(ABC):
```

Decorate the 4 stub methods with `@abstractmethod` and replace stub bodies with `...`:

```python
    @abstractmethod
    def pif_instructions(self) -> str:
        ...

    @abstractmethod
    def handle_entry(self, comment: Any, user: Any, command_parts: list[str]) -> None:
        ...

    @abstractmethod
    def determine_winner(self) -> None:
        ...

    @abstractmethod
    def generate_winner_comment(self) -> str:
        ...
```

Remove the old `print("Implement in subclass")` lines. The `is_already_entered`, `handle_comment`, `finalize`, and `initialize` methods remain concrete.

- [ ] **Step 2: Add abstract method stubs in karma_only_pif.py**

Add no-op implementations with docstrings in `KarmaOnly`:

```python
    def handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None:
        """Not used for KarmaOnly PIFs — entry logic is in handle_comment."""

    def determine_winner(self) -> None:
        """Not used for KarmaOnly PIFs — no winner determination needed."""

    def generate_winner_comment(self) -> str:
        """Not used for KarmaOnly PIFs — no winner announcement needed."""
        return ""
```

These methods already exist in the class hierarchy — KarmaOnly's parent `BasePIF` had stub implementations that were never called. Now they're explicitly documented no-ops.

- [ ] **Step 3: Verify ABC works**

```bash
uv run python3 -c "from pifs.base_pif import BasePIF; print('ABC OK')"
uv run python3 -c "from pifs.karma_only_pif import KarmaOnly; print('KarmaOnly OK')"
uv run python3 -c "
from pifs.lottery_pif import Lottery
from pifs.range_pif import Range
from pifs.poker_pif import Poker
from pifs.infinite_poker_pif import InfinitePoker
from pifs.holdem_poker_pif import HoldemPoker
from pifs.geo_pif import Geo
from pifs.battleship_pif import Battleship
from pifs.randomizer_pif import Randomizer
print('All subclasses OK')
"
```

Expected: all print statements succeed, no `TypeError: Can't instantiate abstract class`.

- [ ] **Step 4: Run mypy on base_pif.py and karma_only_pif.py**

```bash
uv run mypy pifs/base_pif.py pifs/karma_only_pif.py
```

Expected: Success. The only `unused-ignore` errors should be the 5 pre-existing ones in base_pif.py (from pydantic-models branch).

- [ ] **Step 5: Commit** — SKIP THIS. Do NOT commit.

---

### Task 1: Annotate karma_only_pif.py, randomizer_pif.py, lottery_pif.py

**Files:**
- Modify: `pifs/karma_only_pif.py`
- Modify: `pifs/randomizer_pif.py`
- Modify: `pifs/lottery_pif.py`

These 3 are the simplest subclasses: short files, minimal imports, no poker_util dependency.

- [ ] **Step 1: Annotate karma_only_pif.py**

Add `from __future__ import annotations` after the docstring block (after `@author: rcurtis` line). Replace imports and annotate functions:

```python
from __future__ import annotations

import logging

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils.karma_calculator import calculate_karma, formatted_karma
from utils.reddit_helper import get_submission
```

Annotate methods:
- `__init__` params: `postId: str`, `authorName: str`, `minKarma: int | str`, `durationHours: int | str`, `endTime: int | str`, `pifOptions: dict[str, Any] | None = None`, `pifEntries: dict[str, Any] | None = None`, `karmaFail: dict[str, Any] | None = None`
- `pif_instructions(self) -> str`
- `is_already_entered(self, user: Redditor, comment: Comment) -> bool`
- `handle_comment(self, comment: Comment) -> None`
- `finalize(self) -> None`

The `calculate_karma(user)` returns `KarmaResult` (tuple of 5 ints). `formatted_karma(user, karma)` returns `str`.

Also add `from typing import Any` for the dict annotations.

- [ ] **Step 2: Annotate randomizer_pif.py**

Add `from __future__ import annotations` after the `@author` docstring. Replace imports:

```python
from __future__ import annotations

import logging
import random

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
```

Annotate methods:
- `__init__` params: same as karma_only_pif.py
- `pif_instructions(self) -> str`
- `handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None`
- `determine_winner(self) -> None`
- `generate_winner_comment(self) -> str`

- [ ] **Step 3: Annotate lottery_pif.py**

Add `from __future__ import annotations` after the license block. Replace imports:

```python
from __future__ import annotations

import logging
import random

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment
```

Annotate methods:
- `__init__` params: same pattern
- `pif_instructions(self) -> str`
- `handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None`
- `determine_winner(self) -> None`
- `generate_winner_comment(self) -> str`

- [ ] **Step 4: Verify all three pass mypy**

```bash
uv run mypy pifs/karma_only_pif.py pifs/randomizer_pif.py pifs/lottery_pif.py
```

Expected: Success — no issues found in 3 source files. If `Comment` or `Redditor` cause import-untyped issues, add `# type: ignore[import-untyped]` to those imports. If `get_comment` return type causes issues (it returns `Comment` but typed as untyped), annotate local vars.

- [ ] **Step 5: Commit** — SKIP THIS. Do NOT commit.

---

### Task 2: Annotate range_pif.py, geo_pif.py

**Files:**
- Modify: `pifs/range_pif.py`
- Modify: `pifs/geo_pif.py`

These two have entry validation logic (range checks, geocoding). Medium complexity.

- [ ] **Step 1: Annotate range_pif.py**

Add `from __future__ import annotations` after the license block. Replace imports:

```python
from __future__ import annotations

from random import randrange

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment
```

Annotate methods:
- `__init__` params: same pattern
- `pif_instructions(self) -> str`
- `handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None`
- `determine_winner(self) -> None`
- `generate_winner_comment(self) -> str`
- `userAlreadyGuessed(self, guess: int) -> str | None`

Note: `userAlreadyGuessed` uses camelCase (pre-existing naming, don't rename).

- [ ] **Step 2: Annotate geo_pif.py**

Add `from __future__ import annotations` after the `@author` docstring. Replace imports:

```python
from __future__ import annotations

import logging
import random

import pandas as pd
from geopy.distance import distance
from geopy.geocoders import Nominatim

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment, user_agent
```

Annotate:
- `geolocator: Nominatim` (already initialized)
- Methods as in Task 1 pattern
- `userAlreadyGuessed(self, guess: str) -> str | None`
- `handle_entry` accesses `guessed_location.address`, `.latitude`, `.longitude` — these are `str`, `float`, `float` from the `geopy` library (no stubs, so mypy won't check)

Also add `from typing import Any` since `pifEntries` values contain nested dicts.

- [ ] **Step 3: Verify both pass mypy**

```bash
uv run mypy pifs/range_pif.py pifs/geo_pif.py
```

Expected: Success — no issues found in 2 source files. If `pandas` or `geopy` cause import-untyped issues, add `# type: ignore[import-untyped]` on those import lines.

- [ ] **Step 4: Commit** — SKIP THIS. Do NOT commit.

---

### Task 3: Annotate battleship_pif.py

**Files:**
- Modify: `pifs/battleship_pif.py`

Longest PIF subclass (312 lines). Has board logic, coordinate parsing, distance calculations.

- [ ] **Step 1: Annotate battleship_pif.py**

Add `from __future__ import annotations` after the `@author` docstring. Replace imports:

```python
from __future__ import annotations

import logging
import random
import string
from math import sqrt

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils.reddit_helper import get_comment
```

Annotate methods:
- `__init__` params: same pattern
- `pif_instructions(self) -> str`
- `is_already_entered(self, user: Redditor, comment: Comment) -> bool`
- `handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None`
- `determine_winner(self) -> None`
- `generate_winner_comment(self) -> str`
- `userAlreadyGuessed(self, guess_col: str, guess_row: int) -> str | None`
- `calc_distance(self, guess_col: int, guess_row: int) -> float`
- `print_board(self) -> str`
- `nautical_ranks: list[str]` on the module-level list
- `nautical_jargon: list[str]` on the module-level list

Also add `from typing import Any` since `pifEntries` values are dicts.

- [ ] **Step 2: Verify mypy**

```bash
uv run mypy pifs/battleship_pif.py
```

Expected: Success — no issues found.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.

---

### Task 4: Annotate poker_pif.py, infinite_poker_pif.py, holdem_poker_pif.py

**Files:**
- Modify: `pifs/poker_pif.py`
- Modify: `pifs/infinite_poker_pif.py`
- Modify: `pifs/holdem_poker_pif.py`

These use `poker_util` functions which are already typed (from types-utils branch). Key types:
- `poker_util.Card` = `list[int | str]`
- `poker_util.new_deck()` returns `list[Card]`
- `poker_util.deal_card(deck)` returns `Card`
- `poker_util.format_card(card)` returns `str`
- `poker_util.order_cards(hand)` returns `list[Card]`
- `poker_util.hand_score(hand)` returns `int`
- `poker_util.determine_hand(hand)` returns `str`

- [ ] **Step 1: Annotate poker_pif.py**

Add `from __future__ import annotations` after the license block. Imports:

```python
from __future__ import annotations

import logging
import random

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils import poker_util
from utils.reddit_helper import get_comment
```

Annotate:
- `__init__` params: same pattern (note: `pifOptions` initialization for deck/shared_cards)
- `pif_instructions(self) -> str`
- `handle_entry(self, comment: Comment, user: Redditor, command_parts: list[str]) -> None`
- `determine_winner(self) -> None`
- `generate_winner_comment(self) -> str`

Also add `from typing import Any` for entry_details dict.

- [ ] **Step 2: Annotate infinite_poker_pif.py**

Same structure as poker_pif.py. Imports:

```python
from __future__ import annotations

import logging
import random

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils import poker_util
from utils.reddit_helper import get_comment
```

Same method annotations as Task 4 Step 1.

- [ ] **Step 3: Annotate holdem_poker_pif.py**

Imports:

```python
from __future__ import annotations

import itertools
import json
import logging
import random

from praw.models import Comment, Redditor  # type: ignore[import-untyped]

from pifs.base_pif import BasePIF
from utils import poker_util
from utils.reddit_helper import get_comment
```

Same method annotations. Note: `hands` is `list[tuple[Card, Card]]` stored as JSON string in pifOptions. The `itertools.combinations(remaining_cards, 2)` produces an iterator of tuples.

Also add `from typing import Any` for entry_details dict.

- [ ] **Step 4: Verify all three pass mypy**

```bash
uv run mypy pifs/poker_pif.py pifs/infinite_poker_pif.py pifs/holdem_poker_pif.py
```

Expected: Success — no issues found.

- [ ] **Step 5: Commit** — SKIP THIS. Do NOT commit.

---

### Task 5: Update pyproject.toml and full smoke test

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove PIF subclasses from mypy ignore_errors**

Current state (lines 56-68):
```toml
[[tool.mypy.overrides]]
module = [
    "pifs.lottery_pif",
    "pifs.range_pif",
    "pifs.poker_pif",
    "pifs.infinite_poker_pif",
    "pifs.holdem_poker_pif",
    "pifs.geo_pif",
    "pifs.battleship_pif",
    "pifs.karma_only_pif",
    "pifs.randomizer_pif",
]
ignore_errors = true
```

Delete the entire override block.

- [ ] **Step 2: Verify all 9 PIF subclasses pass mypy**

```bash
uv run mypy pifs/karma_only_pif.py pifs/randomizer_pif.py pifs/lottery_pif.py pifs/range_pif.py pifs/geo_pif.py pifs/battleship_pif.py pifs/poker_pif.py pifs/infinite_poker_pif.py pifs/holdem_poker_pif.py
```

Expected: Success — no issues found in 9 source files.

- [ ] **Step 3: Full project smoke test**

```bash
uv run mypy .
```

Expected: Only pre-existing `unused-ignore` errors in `base_pif.py` from pydantic-models branch. No new errors.

- [ ] **Step 4: Commit** — SKIP THIS. Do NOT commit.
