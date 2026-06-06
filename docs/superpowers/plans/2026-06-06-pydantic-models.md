# Pydantic Models Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Pydantic `BaseModel` and `TypedDict` types for PIF domain objects, replacing raw dict construction with validated models.

**Architecture:** Create a `PifData(BaseModel)` with all shared PIF fields and a `PifStorageDict(TypedDict)` for storage shapes. `BasePIF` gets a `to_storage_dict()` method. Rename `build_from_ddb_dict` → `build_from_storage_dict`, migrate to `PifData.model_validate()`. Both storage backends use typed dicts instead of manual construction.

**Tech Stack:** pydantic, mypy strict mode

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `pifs/models.py` | Create | `PifData(BaseModel)` + `PifStorageDict(TypedDict)` |
| `pifs/base_pif.py` | Modify | Add `to_storage_dict()`, use types |
| `pifs/pif_builder.py` | Modify | Rename to `build_from_storage_dict`, use `PifData.model_validate()` |
| `utils/storage_protocol.py` | Modify | Type hints for `PifStorageDict` |
| `utils/local_file_storage.py` | Modify | Use `pif_obj.to_storage_dict()` |
| `utils/dynamo_db_storage.py` | Modify | Use `pif_obj.to_storage_dict()` |
| `utils/pif_storage.py` | Modify | Pass through type hints |
| `pyproject.toml` | Modify | Remove `pifs.*` + storage modules from mypy ignore |

---

### Task 1: Create PifData model and PifStorageDict

**Files:**
- Create: `pifs/models.py`

- [ ] **Step 1: Write the models**

```python
from typing import TypedDict

from pydantic import BaseModel, Field


class PifStorageDict(TypedDict):
    SubmissionId: str
    Author: str
    PifType: str
    MinKarma: int
    PifOptions: dict
    PifEntries: dict
    KarmaFail: dict
    PifState: str
    PifWinner: str
    ExpireTime: int


class PifData(BaseModel):
    post_id: str = Field(alias="SubmissionId")
    author_name: str = Field(alias="Author")
    pif_type: str = Field(alias="PifType")
    min_karma: int = Field(alias="MinKarma")
    expire_time: int = Field(alias="ExpireTime")
    pif_options: dict = Field(default_factory=dict, alias="PifOptions")
    pif_entries: dict = Field(default_factory=dict, alias="PifEntries")
    karma_fail: dict = Field(default_factory=dict, alias="KarmaFail")
    pif_state: str = Field(default="open", alias="PifState")
    pif_winner: str = Field(default="TBD", alias="PifWinner")
```

- [ ] **Step 2: Verify the module compiles**

Run: `uv run python3 -m py_compile pifs/models.py`

Expected: PASS

- [ ] **Step 3: Verify round-trip (validate → dump)**

Run:
```bash
uv run python3 -c "
from pifs.models import PifData, PifStorageDict

raw: PifStorageDict = {
    'SubmissionId': 'abc123',
    'Author': 'testuser',
    'PifType': 'lottery',
    'MinKarma': 5,
    'PifOptions': {},
    'PifEntries': {},
    'KarmaFail': {},
    'PifState': 'open',
    'PifWinner': 'TBD',
    'ExpireTime': 9999999999,
}

model = PifData.model_validate(raw, strict=False)
assert model.post_id == 'abc123'
assert model.author_name == 'testuser'
assert model.pif_type == 'lottery'
assert model.min_karma == 5

dumped = model.model_dump(by_alias=True)
for key in PifStorageDict.__annotations__:
    assert key in dumped, f'Missing {key}'

print('Round-trip OK')
"
```

Expected: "Round-trip OK"

---

### Task 2: Update BasePIF with to_storage_dict()

**Files:**
- Modify: `pifs/base_pif.py`

- [ ] **Step 1: Add import and to_storage_dict method**

Add import at top of `base_pif.py`:
```python
from pifs.models import PifStorageDict
```

Add method to `BasePIF` class:
```python
def to_storage_dict(self) -> PifStorageDict:
    return {
        "SubmissionId": self.postId,
        "Author": self.authorName,
        "PifType": self.pifType,
        "MinKarma": self.minKarma,
        "PifOptions": self.pifOptions,
        "PifEntries": self.pifEntries,
        "KarmaFail": self.karmaFail,
        "PifState": self.pifState,
        "PifWinner": self.pifWinner,
        "ExpireTime": self.expireTime,
    }
```

- [ ] **Step 2: Verify compilation**

Run: `uv run python3 -m py_compile pifs/base_pif.py`

Expected: PASS

---

### Task 3: Update LocalFileStorage to use to_storage_dict()

**Files:**
- Modify: `utils/local_file_storage.py`

- [ ] **Step 1: Replace manual dict construction with to_storage_dict()**

Change `save_pif` method from:
```python
def save_pif(self, pif_obj):
    logging.debug("Storing PIF [%s] to local file", pif_obj.postId)
    with self._lock:
        self._cache[pif_obj.postId] = {
            "SubmissionId": pif_obj.postId,
            "Author": pif_obj.authorName,
            ...
        }
        self._flush()
```

To:
```python
def save_pif(self, pif_obj):
    logging.debug("Storing PIF [%s] to local file", pif_obj.postId)
    with self._lock:
        self._cache[pif_obj.postId] = pif_obj.to_storage_dict()
        self._flush()
```

- [ ] **Step 2: Verify compilation**

Run: `uv run python3 -m py_compile utils/local_file_storage.py`

Expected: PASS

---

### Task 4: Update DynamoDBStorage to use to_storage_dict()

**Files:**
- Modify: `utils/dynamo_db_storage.py`

- [ ] **Step 1: Replace manual dict construction with to_storage_dict()**

Change `save_pif` method from:
```python
def save_pif(self, pif_obj):
    logging.debug("Storing PIF [%s] to DDB", pif_obj.postId)
    self.table.put_item(
        Item={
            "SubmissionId": pif_obj.postId,
            "Author": pif_obj.authorName,
            ...
        }
    )
```

To:
```python
def save_pif(self, pif_obj):
    logging.debug("Storing PIF [%s] to DDB", pif_obj.postId)
    self.table.put_item(Item=pif_obj.to_storage_dict())
```

- [ ] **Step 2: Verify compilation**

Run: `uv run python3 -m py_compile utils/dynamo_db_storage.py`

Expected: PASS

---

### Task 5: Rename and rewrite build_from_ddb_dict to use PifData.model_validate()

**Files:**
- Modify: `pifs/pif_builder.py`
- Modify: `utils/pif_storage.py`

The function is now storage-agnostic (used by both DynamoDB and local file backends), so rename it from `build_from_ddb_dict` to `build_from_storage_dict`.

- [ ] **Step 1: Add import to pif_builder.py**

Add at top of `pif_builder.py`:
```python
from pifs.models import PifData
```

- [ ] **Step 2: Rewrite and rename build_from_ddb_dict → build_from_storage_dict**

Replace the function name and body. The new version validates via `PifData.model_validate()`:

```python
def build_from_storage_dict(storage_dict):
    logging.debug("Building PIF object from %s", storage_dict)
    data = PifData.model_validate(storage_dict)
    pifType = data.pif_type

    if pifType == "lottery":
        return Lottery(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "range":
        return Range(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "poker":
        return Poker(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "infinite-poker":
        return InfinitePoker(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "holdem-poker":
        return HoldemPoker(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "geo":
        return Geo(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "battleship":
        return Battleship(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "karma-only":
        return KarmaOnly(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    elif pifType == "randomizer":
        return Randomizer(
            data.post_id, data.author_name, str(data.min_karma), 0,
            str(data.expire_time), data.pif_options,
            data.pif_entries, data.karma_fail,
        )
    else:
        logging.error("Unsupported PIF type [%s]", pifType)
```

- [ ] **Step 3: Update import and call sites in pif_storage.py**

In `utils/pif_storage.py`, change:
```python
from pifs.pif_builder import build_from_ddb_dict
```
To:
```python
from pifs.pif_builder import build_from_storage_dict
```

And replace all 3 calls of `build_from_ddb_dict(...)` with `build_from_storage_dict(...)`.

- [ ] **Step 4: Verify both files compile**

Run:
```bash
uv run python3 -m py_compile pifs/pif_builder.py
uv run python3 -m py_compile utils/pif_storage.py
```

Expected: both PASS

---

### Task 6: Update StorageProtocol type hints

**Files:**
- Modify: `utils/storage_protocol.py`

- [ ] **Step 1: Update abstract methods with type hints**

```python
import abc

from pifs.models import PifStorageDict


class StorageProtocol(abc.ABC):
    @abc.abstractmethod
    def save_pif(self, pif_obj) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_open_pifs(self) -> list[PifStorageDict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_pif(self, post_id: str) -> PifStorageDict | None:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_pifs(self) -> list[PifStorageDict]:
        raise NotImplementedError

    @abc.abstractmethod
    def open_pif_exists(self, post_id: str) -> bool:
        raise NotImplementedError
```

- [ ] **Step 2: Verify compilation**

Run: `uv run python3 -m py_compile utils/storage_protocol.py`

Expected: PASS

---

### Task 7: Update pif_storage.py facade type hints

**Files:**
- Modify: `utils/pif_storage.py`

- [ ] **Step 1: Add type hints to facade functions**

The logic stays the same — just add return type hints:

```python
import logging
import threading

from config import storage_backend, storage_path
from pifs.pif_builder import build_from_ddb_dict

if storage_backend == "dynamodb":
    from utils.dynamo_db_storage import DynamoDBStorage

    _store = DynamoDBStorage()
elif storage_backend == "local":
    from utils.local_file_storage import LocalFileStorage

    _store = LocalFileStorage(path=storage_path)
else:
    raise ValueError(f"Unknown storage_backend: {storage_backend}")

lock = threading.RLock()


def save_pif(pif_obj) -> None:
    with lock:
        logging.debug("Saving PIF [%s]", pif_obj.postId)
        _store.save_pif(pif_obj)


def get_open_pifs() -> list:
    with lock:
        logging.debug("Fetching open PIFs")
        json_pifs = _store.get_open_pifs()
        return [build_from_ddb_dict(j) for j in json_pifs]


def pif_exists(post_id: str) -> bool:
    with lock:
        return _store.open_pif_exists(post_id)


def get_pif(post_id: str):
    with lock:
        d = _store.get_pif(post_id)
        if d is None:
            return None
        return build_from_ddb_dict(d)


def fetch_all_pifs() -> list:
    with lock:
        return [build_from_ddb_dict(j) for j in _store.fetch_all_pifs()]
```

- [ ] **Step 2: Verify compilation**

Run: `uv run python3 -m py_compile utils/pif_storage.py`

Expected: PASS

---

### Task 8: Remove modules from mypy ignore list and verify

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove pifs.* and storage modules**

Edit `pyproject.toml` `[[tool.mypy.overrides]]` — remove:
- `"pifs.*",`
- `"utils.pif_storage",`
- `"utils.dynamo_db_storage",`
- `"utils.local_file_storage",`
- `"utils.storage_protocol",` (if present)

The list should become:
```toml
module = [
    "utils.dynamo_helper",
    "utils.reddit_helper",
    "utils.poker_util",
    "utils.karma_calculator",
    "utils.personality",
    "handlers.*",
    "pifbot",
    "check_comment",
    "finalize",
    "karma",
    "pif_stats",
    "poker",
]
```

- [ ] **Step 2: Run mypy on the newly-typed modules**

Run:
```bash
uv run mypy pifs/models.py pifs/base_pif.py pifs/pif_builder.py \
  utils/storage_protocol.py utils/local_file_storage.py \
  utils/dynamo_db_storage.py utils/pif_storage.py
```

Expected: Success — no issues found. If there are errors, fix them with explicit type annotations or targeted `# type: ignore` comments.

- [ ] **Step 3: Run ruff**

Run: `uv run ruff check pifs/ utils/`

Expected: all checks pass

---

### Task 9: Final smoke test

- [ ] **Step 1: Verify the full round-trip end-to-end**

Run:
```bash
uv run python3 -c "
from pifs.models import PifData, PifStorageDict
from pifs.pif_builder import build_from_storage_dict
from pifs.base_pif import BasePIF

# Create a PifData
data = PifData(
    SubmissionId='test123',
    Author='testuser',
    PifType='lottery',
    MinKarma=5,
    ExpireTime=9999999999,
)

# Convert to storage dict
raw: PifStorageDict = data.model_dump(by_alias=True)

# Rebuild via build_from_storage_dict
pif = build_from_storage_dict(raw)
assert pif is not None
assert pif.postId == 'test123'
assert pif.authorName == 'testuser'
assert pif.pifType == 'lottery'

# Serialize back
dumped = pif.to_storage_dict()
assert dumped['SubmissionId'] == 'test123'
assert dumped['Author'] == 'testuser'
assert dumped['PifType'] == 'lottery'

print('Full round-trip OK')
"
```

Expected: "Full round-trip OK"
