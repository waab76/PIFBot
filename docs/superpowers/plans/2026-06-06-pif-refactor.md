# PIF Subclass Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `pifs/` package to eliminate boilerplate, improve maintainability, and establish clear patterns for adding new PIF types.

**Architecture:** Four independent refactoring tasks: (1) decorator-based PIF registry replacing 9-way if/elif chains in `pif_builder.py`, (2) `__init__` dedup across 9 subclasses using `super().__init__(pifType=..., **kwargs)`, (3) extract karma checking into a focused helper, (4) type aliases for `pifEntries`/`pifOptions` with TypedDict for complex entry structures. Each task is independently mergeable.

**Tech Stack:** Python 3.11 strict mypy, ABC pattern, type aliases, TypedDict.

---

### Task 1: PIF Registry Pattern

**Files:**
- Modify: `pifs/pif_builder.py`
- Modify: `pifs/base_pif.py`
- Modify: all 9 PIF subclass files

Replace the 9-way `if/elif` chains in `build_from_post()` and `build_from_storage_dict()` with a decorator-based registry.

- [ ] **Step 1: Add registry infrastructure to pif_builder.py**

Replace the current imports and `known_pif_types` list with:

```python
import logging
import time
from typing import Any, TypeVar

from pifs.models import PifData, PifStorageDict

T = TypeVar("T", bound="BasePIF")

PIF_REGISTRY: dict[str, type[BasePIF]] = {}


def register_pif(cls: type[T]) -> type[T]:
    """Decorator to register a PIF subclass in the type registry."""
    PIF_REGISTRY[cls.pif_type] = cls
    return cls


def known_pif_types() -> list[str]:
    """Return all registered PIF type names."""
    return list(PIF_REGISTRY.keys())
```

Remove the old `known_pif_types` list and all individual subclass imports (`from pifs.lottery_pif import Lottery`, etc.).

- [ ] **Step 2: Add `pif_type` class attribute to BasePIF**

In `pifs/base_pif.py`, add an abstract class attribute:

```python
class BasePIF(ABC):
    pif_type: str = ""  # overridden by subclasses

    def __init__(
        ...
```

- [ ] **Step 3: Add `@register_pif` decorator to each subclass**

In each of the 9 subclass files, add the decorator import and apply it:

```python
from pifs.pif_builder import register_pif
```

Then add `pif_type` class attribute and `@register_pif` to each class:

```python
@register_pif
class Lottery(BasePIF):
    pif_type = "lottery"
```

Do this for all 9 subclasses:
- `Lottery`: `pif_type = "lottery"`
- `Range`: `pif_type = "range"`
- `Poker`: `pif_type = "poker"`
- `InfinitePoker`: `pif_type = "infinite-poker"`
- `HoldemPoker`: `pif_type = "holdem-poker"`
- `Geo`: `pif_type = "geo"`
- `Battleship`: `pif_type = "battleship"`
- `KarmaOnly`: `pif_type = "karma-only"`
- `Randomizer`: `pif_type = "randomizer"`

- [ ] **Step 4: Simplify build_from_post() to use registry**

Replace the 9-way if/elif chain with:

```python
def build_from_post(submission: Any, line: str) -> Any | None:
    logging.info(
        'Building PIF from command [%s] for submission "%s"', line, submission.title
    )
    try:
        parts = line.split()
        pif_type = parts[1]
        if pif_type not in PIF_REGISTRY:
            return None
        min_karma = parts[2]
        duration_hours = parts[3]
        end_time = int(submission.created_utc) + 3600 * int(duration_hours)

        if end_time < time.time():
            logging.info('PIF "%s" should already be closed', submission.title)
            submission.mod.flair(text="PIF - Closed", css_class="orange")
            submission.mod.lock()

        pif_cls = PIF_REGISTRY[pif_type]
        pif = pif_cls(
            submission.id,
            submission.author.name,
            min_karma,
            duration_hours,
            end_time,
            pifOptions={},
            pifEntries={},
            karmaFail={},
        )
        return pif
    except IndexError:
        logging.error("Not enough PIF parameters in input: [%s]", line)
        submission.reply(f"""Well this is embarassing.
        You said *{line}* and I couldn't figure out how to handle it.
        Maybe check the LatherBot documentation and try again.""")
    return None
```

Note: The `range` type needs `RangeMin`/`RangeMax` from `parts[4:6]`. This is the one type that needs special handling. Add a check:

```python
        pif_cls = PIF_REGISTRY[pif_type]
        pif_options: dict[str, Any] = {}
        if pif_type == "range":
            range_min = int(parts[4])
            range_max = int(parts[5])
            if range_max <= range_min:
                submission.reply("I think you got your min and max mixed up")
            pif_options["RangeMin"] = range_min
            pif_options["RangeMax"] = range_max

        pif = pif_cls(
            submission.id,
            submission.author.name,
            min_karma,
            duration_hours,
            end_time,
            pifOptions=pif_options,
            pifEntries={},
            karmaFail={},
        )
```

- [ ] **Step 5: Simplify build_from_storage_dict() to use registry**

Replace the 9-way if/elif chain with:

```python
def build_from_storage_dict(storage_dict: PifStorageDict) -> BasePIF | None:
    logging.debug("Building PIF object from %s", storage_dict)
    data = PifData.model_validate(storage_dict)
    pif_type = data.pif_type

    if pif_type not in PIF_REGISTRY:
        logging.error("Unsupported PIF type [%s]", pif_type)
        return None

    pif_cls = PIF_REGISTRY[pif_type]
    return pif_cls(
        data.post_id,
        data.author_name,
        str(data.min_karma),
        0,
        str(data.expire_time),
        data.pif_options,
        data.pif_entries,
        data.karma_fail,
    )
```

- [ ] **Step 6: Update callers of `known_pif_types`**

`known_pif_types` is now a function, not a list. Update all call sites:
- `pif_stats.py`: `for pif_type in pif_builder.known_pif_types:` → `for pif_type in pif_builder.known_pif_types():`
- `handlers/submission_handler.py`: `if parts[1] in pif_builder.known_pif_types:` → `if parts[1] in pif_builder.known_pif_types():`

- [ ] **Step 7: Verify mypy and imports**

```bash
uv run python3 -c "from pifs.pif_builder import PIF_REGISTRY, known_pif_types; print(known_pif_types())"
uv run mypy pifs/pif_builder.py pifs/base_pif.py pif_stats.py handlers/submission_handler.py
```

Expected: All 9 types registered. Mypy passes.

- [ ] **Step 8: Commit** — SKIP THIS. Do NOT commit.

---

### Task 2: __init__ Dedup Across Subclasses

**Files:**
- Modify: all 9 PIF subclass files

All 9 subclasses copy-paste the same 8-parameter `__init__` and `BasePIF.__init__()` call. Replace with `super().__init__(pifType=..., **kwargs)`.

- [ ] **Step 1: Update BasePIF.__init__ to accept **kwargs**

In `pifs/base_pif.py`, the current `__init__` signature is:

```python
def __init__(
    self,
    postId: str,
    authorName: str,
    pifType: str,
    minKarma: int | str,
    durationHours: int | str,
    endTime: int | str,
    pifOptions: dict[str, Any] | None = None,
    pifEntries: dict[str, Any] | None = None,
    karmaFail: dict[str, Any] | None = None,
):
```

Keep this signature as-is. The subclasses will use `super().__init__(...)` instead of `BasePIF.__init__(self, ...)`.

- [ ] **Step 2: Simplify each subclass __init__**

Current pattern (example from Lottery):

```python
def __init__(
    self,
    postId: str,
    authorName: str,
    minKarma: int | str,
    durationHours: int | str,
    endTime: int | str,
    pifOptions: dict[str, Any] = {},
    pifEntries: dict[str, Any] = {},
    karmaFail: dict[str, Any] = {},
) -> None:
    logging.debug("Building lottery PIF [%s]", postId)
    BasePIF.__init__(
        self, postId, authorName, "lottery", minKarma,
        durationHours, endTime, pifOptions, pifEntries, karmaFail,
    )
```

Replace with:

```python
def __init__(
    self,
    postId: str,
    authorName: str,
    minKarma: int | str,
    durationHours: int | str,
    endTime: int | str,
    pifOptions: dict[str, Any] = {},
    pifEntries: dict[str, Any] = {},
    karmaFail: dict[str, Any] = {},
) -> None:
    logging.debug("Building lottery PIF [%s]", postId)
    super().__init__(
        postId=postId,
        authorName=authorName,
        minKarma=minKarma,
        durationHours=durationHours,
        endTime=endTime,
        pifOptions=pifOptions,
        pifEntries=pifEntries,
        karmaFail=karmaFail,
    )
```

Apply to all 9 subclasses. The only difference per subclass is the log message string.

Note: `super().__init__()` uses keyword arguments. Since `BasePIF.__init__` accepts positional args, this is compatible. The `pifType` is not passed — subclasses set it via the `pif_type` class attribute, but `BasePIF.__init__` still needs it. So we need to pass `pifType=self.pif_type` in the super call:

```python
    super().__init__(
        postId=postId,
        authorName=authorName,
        pifType=self.pif_type,
        minKarma=minKarma,
        ...
    )
```

Wait, `self.pif_type` is a class attribute, so `self.pif_type` works in `__init__`. But `super().__init__()` is called before `self` is fully initialized. Actually, `self` exists at this point — `__init__` is called after `__new__` creates the instance. So `self.pif_type` is accessible. But this is fragile — the class attribute lookup works but it's not the cleanest pattern.

Better approach: keep passing the string directly in `super().__init__()`:

```python
    super().__init__(
        postId=postId,
        authorName=authorName,
        pifType="lottery",
        minKarma=minKarma,
        durationHours=durationHours,
        endTime=endTime,
        pifOptions=pifOptions,
        pifEntries=pifEntries,
        karmaFail=karmaFail,
    )
```

This is still cleaner than the current `BasePIF.__init__(self, ...)` pattern — it uses `super()` and keyword args, and the string literal is the only per-subclass customization.

Apply to all 9 subclasses.

- [ ] **Step 3: Verify all subclasses instantiate correctly**

```bash
uv run python3 -c "
from pifs.pif_builder import PIF_REGISTRY, known_pif_types
for t in known_pif_types():
    cls = PIF_REGISTRY[t]
    pif = cls('test123', 'testuser', 100, 24, 9999999999)
    print(f'{t}: OK (pifType={pif.pifType})')
"
```

Expected: All 9 types instantiate with correct `pifType`.

- [ ] **Step 4: Verify mypy**

```bash
uv run mypy pifs/base_pif.py pifs/lottery_pif.py pifs/range_pif.py pifs/poker_pif.py pifs/infinite_poker_pif.py pifs/holdem_poker_pif.py pifs/geo_pif.py pifs/battleship_pif.py pifs/karma_only_pif.py pifs/randomizer_pif.py
```

Expected: Success — no issues found in 10 source files.

- [ ] **Step 5: Commit** — SKIP THIS. Do NOT commit.

---

### Task 3: Extract Karma Checking from BasePIF.handle_comment

**Files:**
- Create: `pifs/karma_checker.py`
- Modify: `pifs/base_pif.py`

`BasePIF.handle_comment()` is ~100 lines doing command parsing, karma calculation, blacklist checking, and dispatch. Extract karma checking into a focused helper.

- [ ] **Step 1: Create karma_checker.py**

```python
from __future__ import annotations

import logging
from typing import Any

from config import blacklist
from utils.karma_calculator import calculate_karma, formatted_karma


class KarmaCheckResult:
    """Result of a karma check for a user."""

    def __init__(
        self,
        passed: bool,
        user: Any,
        reason: str = "",
        karma: tuple[int, int, int, int, int] | None = None,
        formatted_karma: str | None = None,
    ):
        self.passed = passed
        self.user = user
        self.reason = reason  # "blacklisted", "karma_failed", "calculation_error", ""
        self.karma = karma
        self.formatted_karma = formatted_karma


def check_karma(
    user: Any, min_karma: int, pif_id: str
) -> KarmaCheckResult:
    """Check if a user meets the minimum karma requirement.

    Args:
        user: PRAW Redditor object.
        min_karma: Minimum karma required.
        pif_id: PIF post ID for logging.

    Returns:
        KarmaCheckResult with pass/fail status, reason, and karma details.
    """
    if user.name in blacklist:
        logging.info(
            "User %s is on the PIF blacklist [%s]",
            user.name, pif_id,
        )
        return KarmaCheckResult(
            passed=False, user=user, reason="blacklisted",
        )

    karma = calculate_karma(user)
    if not karma:
        logging.error(
            "Failed to calculate karma for user %s [%s]",
            user.name, pif_id,
        )
        return KarmaCheckResult(
            passed=False, user=user, reason="calculation_error",
        )

    passed = karma[0] >= min_karma
    formatted = formatted_karma(user, karma)

    return KarmaCheckResult(
        passed=passed,
        user=user,
        reason="" if passed else "karma_failed",
        karma=karma,
        formatted_karma=formatted,
    )
```

- [ ] **Step 2: Update BasePIF.handle_comment to use KarmaChecker**

In `pifs/base_pif.py`, replace the karma checking block in `handle_comment()` (the section that calls `calculate_karma`, checks blacklist, and builds `formattedKarma`) with a call to `check_karma()`:

Current code in handle_comment (around lines 62-140):
```python
                user = comment.author
                karma = (1, 1, 1, 1, 1) if self.minKarma < 1 else calculate_karma(user)
                if not karma:
                    comment.reply(
                        f"I cannot seem to calculate karma for user u/{user.name}"
                    )
                    comment.save()
                    return False
                formattedKarma = formatted_karma(user, karma)

                if parts[1].startswith("in"):
                    if self.is_already_entered(user, comment):
                        ...
                    elif user.name in blacklist:
                        ...
                    elif karma[0] >= self.minKarma:
                        ...
```

Replace with:
```python
                user = comment.author
                karma_result = check_karma(user, self.minKarma, self.postId)

                if karma_result.reason == "calculation_error":
                    comment.reply(
                        f"I cannot seem to calculate karma for user u/{user.name}"
                    )
                    comment.save()
                    return False

                if parts[1].startswith("in"):
                    if self.is_already_entered(user, comment):
                        ...
                    elif karma_result.reason == "blacklisted":
                        logging.info(
                            "User %s is blacklisted for PIF [%s]",
                            user.name, self.postId,
                        )
                        self.karmaFail[user.name] = comment.id
                        comment.reply("Sorry, you're on the PIF blacklist")
                        comment.save()
                        return False
                    elif not karma_result.passed:
                        comment.reply(karma_result.formatted_karma)
                        comment.save()
                        self.karmaFail[user.name] = comment.id
                        return False
                    else:
                        self.handle_entry(comment, user, parts)
                        comment.reply(karma_result.formatted_karma)
                        comment.save()
                        return True
```

Also replace the karma check section (around lines 140-170):
```python
                elif parts[1].startswith("karma"):
                    comment.reply(karma_result.formatted_karma)
                    comment.save()
                    return True
```

- [ ] **Step 3: Remove unused imports from base_pif.py**

After the refactor, `base_pif.py` no longer needs:
- `from config import blacklist`
- `from utils.karma_calculator import calculate_karma, formatted_karma`

Remove these imports. Add:
```python
from pifs.karma_checker import check_karma
```

- [ ] **Step 4: Verify karma_checker.py passes mypy**

```bash
uv run mypy pifs/karma_checker.py
```

Expected: Success — no issues found.

- [ ] **Step 5: Verify base_pif.py passes mypy**

```bash
uv run mypy pifs/base_pif.py
```

Expected: Success — no issues found.

- [ ] **Step 6: Verify all subclasses still work**

```bash
uv run mypy pifs/lottery_pif.py pifs/range_pif.py pifs/poker_pif.py pifs/infinite_poker_pif.py pifs/holdem_poker_pif.py pifs/geo_pif.py pifs/battleship_pif.py pifs/karma_only_pif.py pifs/randomizer_pif.py
```

Expected: Success — no issues found.

- [ ] **Step 7: Commit** — SKIP THIS. Do NOT commit.

---

### Task 4: Type Aliases for pifEntries and pifOptions

**Files:**
- Modify: `pifs/models.py`
- Modify: `pifs/base_pif.py`

Define type aliases for the polymorphic `pifEntries` and `pifOptions` dicts. Add TypedDict for the most complex entry structures.

- [ ] **Step 1: Add type aliases to models.py**

In `pifs/models.py`, add after the existing imports:

```python
from typing import Any, TypedDict


class EntryDict(TypedDict, total=False):
    """Base entry dict — each PIF type stores different fields.

    Common fields:
    - CommentId: str — the Reddit comment ID for the entry

    PIF-specific fields:
    - Range: Guess (int)
    - Geo: Guess (str), GuessAddr (str), GuessLatLon (str)
    - Battleship: GuessTime (int), GuessCol (str), GuessRow (int)
    - Poker: UserCards (list[Card]), UserHand (list[Card]), HandScore (int)
    - InfinitePoker: UserHand (list[Card]), HandScore (int)
    - HoldemPoker: UserHoleCards (list[Card]), BestHand (list[Card]), HandScore (int)
    - Lottery/Randomizer: no additional fields (value is just comment ID)
    """
    CommentId: str
    Guess: int
    GuessAddr: str
    GuessLatLon: str
    GuessTime: int
    GuessCol: str
    GuessRow: int
    UserCards: list[Any]
    UserHand: list[Any]
    HandScore: int
    UserHoleCards: list[Any]
    BestHand: list[Any]


class OptionsDict(TypedDict, total=False):
    """PIF options dict — each PIF type stores different configuration.

    PIF-specific fields:
    - Range: RangeMin (int), RangeMax (int)
    - Poker: Deck (list[Card]), SharedCards (list[Card])
    - InfinitePoker: no options
    - HoldemPoker: FlopCards (list[Card]), RiverCard (Card), TurnCard (Card), ExtraInfo (str), hands (str JSON)
    - Geo: WinLatLon (str)
    - Battleship: Board (list[list[str]]), NorthSouth (int), StartRow (int), StartCol (int)
    - Lottery/Randomizer/KarmaOnly: no options
    """
    RangeMin: int
    RangeMax: int
    Deck: list[Any]
    SharedCards: list[Any]
    FlopCards: list[Any]
    RiverCard: list[Any]
    TurnCard: list[Any]
    ExtraInfo: str
    hands: str
    WinLatLon: str
    Board: list[list[str]]
    NorthSouth: int
    StartRow: int
    StartCol: int
```

- [ ] **Step 2: Update BasePIF to use the new types**

In `pifs/base_pif.py`, update the `__init__` signature:

```python
from pifs.models import EntryDict, OptionsDict, PifStorageDict

class BasePIF(ABC):
    ...
    def __init__(
        self,
        postId: str,
        authorName: str,
        pifType: str,
        minKarma: int | str,
        durationHours: int | str,
        endTime: int | str,
        pifOptions: OptionsDict | None = None,
        pifEntries: dict[str, EntryDict | str] | None = None,
        karmaFail: dict[str, str] | None = None,
    ):
        ...
        self.pifOptions: OptionsDict = pifOptions or {}
        self.pifEntries: dict[str, EntryDict | str] = pifEntries or {}
        self.karmaFail: dict[str, str] = karmaFail or {}
```

Note: `pifEntries` values can be either `EntryDict` (for most types) or `str` (for Lottery/Randomizer which store just the comment ID). `karmaFail` values are comment IDs (strings).

- [ ] **Step 3: Update PifStorageDict in models.py**

The `PifStorageDict` TypedDict should use the new types:

Current:
```python
class PifStorageDict(TypedDict):
    ...
    PifOptions: dict[str, Any]
    PifEntries: dict[str, Any]
    KarmaFail: dict[str, Any]
```

Update to:
```python
class PifStorageDict(TypedDict):
    ...
    PifOptions: OptionsDict
    PifEntries: dict[str, EntryDict | str]
    KarmaFail: dict[str, str]
```

- [ ] **Step 4: Verify mypy on all pifs files**

```bash
uv run mypy pifs/
```

Expected: Success — no issues found. If there are type errors in the subclasses accessing `pifOptions` or `pifEntries`, add `# type: ignore[typeddict-item]` where needed, or adjust the TypedDict fields.

- [ ] **Step 5: Commit** — SKIP THIS. Do NOT commit.

---

### Task 5: Full project smoke test

- [ ] **Step 1: Run full project mypy**

```bash
uv run mypy .
```

Expected: Success — no issues found.

- [ ] **Step 2: Verify all PIF types can be built**

```bash
uv run python3 -c "
from pifs.pif_builder import PIF_REGISTRY, known_pif_types
for t in known_pif_types():
    cls = PIF_REGISTRY[t]
    pif = cls('test123', 'testuser', 100, 24, 9999999999)
    print(f'{t}: OK (pifType={pif.pifType}, pif_type={pif.pif_type})')
"
```

Expected: All 9 types instantiate with correct `pifType` and `pif_type`.

- [ ] **Step 3: Commit** — SKIP THIS. Do NOT commit.
