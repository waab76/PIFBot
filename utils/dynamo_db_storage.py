import logging
import boto3
from boto3.dynamodb.conditions import Attr, Key

from utils.storage_protocol import StorageProtocol


class DynamoDBStorage(StorageProtocol):
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('PIFs')

    def save_pif(self, pif_obj):
        logging.debug('Storing PIF [%s] to DDB', pif_obj.postId)
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
