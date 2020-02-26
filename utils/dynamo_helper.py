import boto3
import logging

from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource('dynamodb')
pifTable = dynamodb.Table('PIFs')

def save_pif(pif_obj):
    logging.debug('Storing PIF [%s] to DDB', pif_obj.postId)
    pifTable.put_item(
        Item={
            'SubmissionId': pif_obj.postId,
            'Author': pif_obj.authorName,
            'PifType': pif_obj.pifType,
            'MinKarma': pif_obj.minKarma,
            'PifOptions': pif_obj.pifOptions,
            'PifEntries': pif_obj.pifEntries,
            'PifState': pif_obj.pifState,
            'PifWinner': pif_obj.pifWinner,
            'ExpireTime': pif_obj.expireTime
        }
    )

def fetch_open_pifs():
    logging.debug('Fetching open PIFs from DDB')
    response = pifTable.scan(FilterExpression=Attr('PifState').eq('open'))
    if len(response['Items']) > 0:
        return response['Items']
    else:
        return []

def fetch_closed_pifs():
    logging.debug('Fetching open PIFs from DDB')
    response = pifTable.scan(FilterExpression=Attr('PifState').eq('closed'))
    if len(response['Items']) > 0:
        return response['Items']
    else:
        return []

def fetch_all_pifs():
    logging.debug('Fetching open PIFs from DDB')
    response = pifTable.scan()
    if len(response['Items']) > 0:
        return response['Items']
    else:
        return []

def fetch_pif(post_id):
    logging.debug('Fetching PIF [%s] from DDB', post_id)
    response = pifTable.query(
            KeyConditionExpression=Key('SubmissionId').eq(post_id)
    )
    if len(response['Items']) > 0:
        return response['Items'][0]
    else:
        logging.info('PIF [%s] not found in DDB', post_id)
        return None

def open_pif_exists(post_id):
    ddb_dict = fetch_pif(post_id)
    return (None is not ddb_dict and 'open' == ddb_dict['PifState']) 
