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
        try:
            with open(self.path, 'r') as f:
                self._cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = {}

    def _flush(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except OSError as e:
            logging.error('Failed to write PIF storage to %s: %s', self.path, e)

    def save_pif(self, pif_obj):
        logging.debug('Storing PIF [%s] to local file', pif_obj.postId)
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
        with self._lock:
            pif = self._cache.get(post_id)
        return pif is not None and pif['PifState'] == 'open'
