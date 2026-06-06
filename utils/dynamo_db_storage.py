import logging
from typing import Any

import boto3  # type: ignore[import-untyped]
from boto3.dynamodb.conditions import Attr, Key  # type: ignore[import-untyped]

from pifs.models import PifStorageDict
from utils.storage_protocol import StorageProtocol


class DynamoDBStorage(StorageProtocol):
    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table("PIFs")

    def save_pif(self, pif_obj: Any) -> None:
        logging.debug("Storing PIF [%s] to DDB", pif_obj.postId)
        self.table.put_item(Item=pif_obj.to_storage_dict())

    def get_open_pifs(self) -> list[PifStorageDict]:
        logging.debug("Fetching open PIFs from DDB")
        response = self.table.scan(FilterExpression=Attr("PifState").eq("open"))
        return response.get("Items", [])  # type: ignore[no-any-return]

    def get_pif(self, post_id: str) -> PifStorageDict | None:
        logging.debug("Fetching PIF [%s] from DDB", post_id)
        response = self.table.query(
            KeyConditionExpression=Key("SubmissionId").eq(post_id)
        )
        items = response.get("Items", [])
        if items:
            return items[0]  # type: ignore[no-any-return]
        logging.debug("PIF [%s] not found in DDB", post_id)
        return None

    def fetch_all_pifs(self) -> list[PifStorageDict]:
        logging.debug("Fetching all PIFs from DDB")
        response = self.table.scan()
        return response.get("Items", [])  # type: ignore[no-any-return]

    def open_pif_exists(self, post_id: str) -> bool:
        ddb_dict = self.get_pif(post_id)
        return ddb_dict is not None and ddb_dict["PifState"] == "open"
