import logging

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


def save_pif(pif_obj):
    logging.debug("Saving PIF [%s]", pif_obj.postId)
    _store.save_pif(pif_obj)


def get_open_pifs():
    logging.debug("Fetching open PIFs")
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
    return [build_from_ddb_dict(j) for j in _store.fetch_all_pifs()]
