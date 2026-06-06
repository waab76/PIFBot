# Pluggable Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) for syntax tracking.

**Goal:** Replace hardcoded DynamoDB dependency with pluggable storage (ABC + DynamoDB + LocalFile backends), zero changes to handlers or PIF types.

**Architecture:** Define `StorageProtocol` ABC in new file. Refactor `dynamo_helper.py` into `DynamoDBStorage(StorageProtocol)` class. Build `LocalFileStorage(StorageProtocol)` writing JSON to disk. Rewrite `utils/pif_storage.py` facade to select backend via `config.storage_backend`. Fix `pif_stats.py` to use facade instead of direct `dynamo_helper` import.

**Tech Stack:** Python stdlib `abc`, `json`, `os`, `logging`. No new external deps. boto3 stays optional (only imported when dynamodb backend selected).

**Key constraint:** Handlers import `from utils.pif_storage import get_pif, save_pif, pif_exists, get_open_pifs` — these 4 function names MUST stay identical. No handler changes.

---

### Task 1: Create `utils/storage_protocol.py` — ABC

**Files:**
- Create: `utils/storage_protocol.py`

- [ ] **Step 1: Write the file**

```python
import abc


class StorageProtocol(abc.ABC):
    @abc.abstractmethod
    def save_pif(self, pif_obj):
        raise NotImplementedError

    @abc.abstractmethod
    def get_open_pifs(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_pif(self, post_id):
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_pifs(self):
        raise NotImplementedError

    @abc.abstractmethod
    def open_pif_exists(self, post_id):
        raise NotImplementedError
```

Methods mirror the 5 operations callers use:
- `save_pif(pif_obj)` — serialize and persist
- `get_open_pifs()` — return `List[dict]` with `PifState == 'open'`
- `get_pif(post_id)` — return `dict | None` by key
- `fetch_all_pifs()` — return `List[dict]` unconditionally (for stats)
- `open_pif_exists(post_id)` — `bool` shortcut

Returning `dict` (not PIF objects) keeps deserialization in the facade only.

- [ ] **Step 2: Verify file parses**

Run: `python3 -c "from utils.storage_protocol import StorageProtocol; print('OK')"`
Expected: `OK`

---

### Task 2: Refactor `utils/dynamo_helper.py` → `utils/dynamo_db_storage.py`

**Files:**
- Rename: `utils/dynamo_helper.py` → `utils/dynamo_db_storage.py`
- Modify: `utils/dynamo_db_storage.py:1-83` (full rewrite)
- Modify: `utils/pif_storage.py:23` (update import path)

- [ ] **Step 1: Rewrite `utils/dynamo_db_storage.py`**

Replace flat module with class implementing `StorageProtocol`. Keep `boto3` import lazy (inside constructor) so non-DynamoDB users never need boto3.

```python
import logging
import boto3
from boto3.dynamodb.conditions import Attr, Key

from utils.storage_protocol import StorageProtocol


class DynamoDBStorage(StorageProtocol):
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('PIFs')

    def save_pif(self, pif_obj):
        logging.info('Storing PIF [%s] to DDB', pif_obj.postId)
        self.table.put_item(
            Item={
                'SubmissionId': pif_obj.postId,
                'Author': pif_obj.authorName,
                'PifType': pif_obj.pifType,
                'MinKarma': pif_obj.minKarma,
                'PifOptions': pif_obj.pifOptions,
                'PifEntries': pif_obj.pifEntries,
                'KarmaFail': pif_obj.karmaFail,
                'PifState': pif_obj.pifState,
                'PifWinner': pif_obj.pifWinner,
                'ExpireTime': pif_obj.expireTime
            }
        )

    def get_open_pifs(self):
        logging.debug('Fetching open PIFs from DDB')
        response = self.table.scan(FilterExpression=Attr('PifState').eq('open'))
        return response.get('Items', [])

    def get_pif(self, post_id):
        logging.debug('Fetching PIF [%s] from DDB', post_id)
        response = self.table.query(
            KeyConditionExpression=Key('SubmissionId').eq(post_id)
        )
        items = response.get('Items', [])
        if items:
            return items[0]
        logging.debug('PIF [%s] not found in DDB', post_id)
        return None

    def fetch_all_pifs(self):
        logging.debug('Fetching all PIFs from DDB')
        response = self.table.scan()
        return response.get('Items', [])

    def open_pif_exists(self, post_id):
        ddb_dict = self.get_pif(post_id)
        return ddb_dict is not None and ddb_dict['PifState'] == 'open'
```

Note: `fetch_closed_pifs` was in the original but never called anywhere. Omitted per YAGNI. The `response.get('Items', [])` pattern replaces the verbose `if len(...) > 0 ... else []` pattern for concision while remaining identical behavior.

- [ ] **Step 2: Delete old file**

```bash
rm utils/dynamo_helper.py
```

- [ ] **Step 3: Verify new file parses**

Run: `python3 -c "from utils.dynamo_db_storage import DynamoDBStorage; print('OK')"`
Expected: `OK` (will fail at boto3 resource init, but import should succeed)

---

### Task 3: Build `utils/local_file_storage.py`

**Files:**
- Create: `utils/local_file_storage.py`

- [ ] **Step 1: Write the file**

```python
import json
import logging
import os
import threading

from utils.storage_protocol import StorageProtocol


class LocalFileStorage(StorageProtocol):
    def __init__(self, path='/tmp/pifbot_storage/pifs.json'):
        self.path = path
        self._lock = threading.Lock()
        self._cache = None
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self._cache = json.load(f)
        else:
            self._cache = {}

    def _flush(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self._cache, f, indent=2)

    def save_pif(self, pif_obj):
        logging.info('Storing PIF [%s] to local file', pif_obj.postId)
        with self._lock:
            self._cache[pif_obj.postId] = {
                'SubmissionId': pif_obj.postId,
                'Author': pif_obj.authorName,
                'PifType': pif_obj.pifType,
                'MinKarma': pif_obj.minKarma,
                'PifOptions': pif_obj.pifOptions,
                'PifEntries': pif_obj.pifEntries,
                'KarmaFail': pif_obj.karmaFail,
                'PifState': pif_obj.pifState,
                'PifWinner': pif_obj.pifWinner,
                'ExpireTime': pif_obj.expireTime
            }
            self._flush()

    def get_open_pifs(self):
        with self._lock:
            return [v for v in self._cache.values() if v['PifState'] == 'open']

    def get_pif(self, post_id):
        with self._lock:
            return self._cache.get(post_id)

    def fetch_all_pifs(self):
        with self._lock:
            return list(self._cache.values())

    def open_pif_exists(self, post_id):
        pif = self.get_pif(post_id)
        return pif is not None and pif['PifState'] == 'open'
```

Dict shape matches exactly what `dynamo_helper.py` wrote to DynamoDB — same keys (`SubmissionId`, `Author`, `PifType`, etc.) — so `build_from_ddb_dict` in `pif_builder.py` works unchanged.

Thread lock protects concurrent access from multiple handler threads. Save is mutating; get/fetch use shared lock for consistency.

- [ ] **Step 2: Verify file parses**

Run: `python3 -c "from utils.local_file_storage import LocalFileStorage; print('OK')"`
Expected: `OK`

---

### Task 4: Rewrite `utils/pif_storage.py` facade

**Files:**
- Modify: `utils/pif_storage.py:1-68` (full rewrite)

- [ ] **Step 1: Rewrite file**

```python
import logging

from config import storage_backend, storage_path
from pifs.pif_builder import build_from_ddb_dict

if storage_backend == 'dynamodb':
    from utils.dynamo_db_storage import DynamoDBStorage
    _store = DynamoDBStorage()
elif storage_backend == 'local':
    from utils.local_file_storage import LocalFileStorage
    _store = LocalFileStorage(path=storage_path)
else:
    raise ValueError("Unknown storage_backend: {}".format(storage_backend))

def save_pif(pif_obj):
    logging.debug('Saving PIF [%s]', pif_obj.postId)
    _store.save_pif(pif_obj)

def get_open_pifs():
    logging.debug('Fetching open PIFs')
    json_pifs = _store.get_open_pifs()
    return [build_from_ddb_dict(j) for j in json_pifs]

def pif_exists(post_id):
    return _store.open_pif_exists(post_id)

def get_pif(post_id):
    d = _store.get_pif(post_id)
    if d is None:
        return None
    return build_from_ddb_dict(d)

def fetch_all_pifs():
    return _store.fetch_all_pifs()
```

Public API preserved exactly: `save_pif`, `get_open_pifs`, `pif_exists`, `get_pif` — all handlers keep working. Added `fetch_all_pifs` for `pif_stats.py`.

Backend selection happens once at import time. No runtime switching needed.

- [ ] **Step 2: Verify file parses**

Run: `python3 -c "from utils.pif_storage import save_pif, get_open_pifs, pif_exists, get_pif; print('OK')"` — this will fail until config.py has `storage_backend` and `storage_path`. That's fine; we add those in Task 6. For now verify syntax:

```bash
python3 -c "compile(open('utils/pif_storage.py').read(), 'utils/pif_storage.py', 'exec'); print('syntax OK')"
```

Expected: `syntax OK`

---

### Task 5: Fix `pif_stats.py` to use facade

**Files:**
- Modify: `pif_stats.py:25,29`

- [ ] **Step 1: Change import and fetch line**

Replace `from utils import dynamo_helper` (line 25) with nothing — not needed. Replace `pif_list = dynamo_helper.fetch_all_pifs()` (line 29) with `from utils.pif_storage import fetch_all_pifs` at the top, then `pif_list = fetch_all_pifs()`.

Edit `pif_stats.py:25`:
```python
# Remove this line:
from utils import dynamo_helper
```

Edit `pif_stats.py:29`:
```python
# Change this line:
pif_list = dynamo_helper.fetch_all_pifs()
# To this:
from utils.pif_storage import fetch_all_pifs\npif_list = fetch_all_pifs()
```

Final state after both edits — the top of the file becomes:

```python
import time

from pifs import pif_builder
from utils import reddit_helper
from utils import poker_util
from utils.pif_storage import fetch_all_pifs

pif_list = fetch_all_pifs()
```

- [ ] **Step 2: Verify syntax**

```bash
python3 -c "compile(open('pif_stats.py').read(), 'pif_stats.py', 'exec'); print('syntax OK')"
```

Expected: `syntax OK`

---

### Task 6: Update `config.py` (gitignored)

**Files:**
- Modify: `config.py` (gitignored, must be created/edited by developer)

- [ ] Step 1: Document required config fields

Add to `config.py`:

```python
storage_backend = 'dynamodb'   # 'dynamodb' or 'local'
storage_path = '/tmp/pifbot_storage/pifs.json'  # only used when backend is 'local'
```

For dev/local use, set `storage_backend = 'local'`.

---

### Self-Review

1. **Spec coverage:**
   - ABC defined → Task 1
   - DynamoDB backend as class → Task 2
   - LocalFile backend → Task 3
   - Facade rewritten with backend selection → Task 4
   - `pif_stats.py` fixed → Task 5
   - Config updated → Task 6
   - No handler changes required ✓

2. **Placeholder scan:** No TBD/TODO/placeholder patterns found.

3. **Type consistency:** All methods return same types as originals. `get_open_pifs` / `get_pif` return dicts (same shape DynamoDB returned). `pif_exists` returns bool. `save_pif` returns None. ABC method signatures match facade and both implementations.

4. **Edge cases:**
   - Thread safety in LocalFileStorage ✓ (threading.Lock)
   - File missing at startup → LocalFileStorage creates empty dict ✓
   - `storage_backend` unknown → raises ValueError ✓
   - boto3 never imported when using local backend ✓ (lazy import inside class)
   - `pif_stats.py` was the only file bypassing facade — fixed ✓
   - `finalize.py` and `gen_map.py` already use facade — no change needed ✓
