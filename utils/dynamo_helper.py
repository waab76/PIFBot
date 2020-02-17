import boto3

from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource('dynamodb')
pifTable = dynamodb.Table('PIFs')

def create_pif_entry(pif_obj):
    pifTable.put_item(
        Item={
            'SubmissionId': pif_obj.postId,
            'Author': pif_obj.authorName,
            'PifType': pif_obj.pifType,
            'MinKarma': pif_obj.minKarma,
            'DurationHours': pif_obj.durationHours,
            'PifOptions': pif_obj.pifOptions,
            'PifEntries': pif_obj.pifEntries,
            'PifState': 'open',
            'ExpireTime': pif_obj.expireTime
        }
    )

def close_pif(post_id):
    pifTable.update_item(
        Key={'SubmissionId': post_id},
        UpdateExpression='SET PifState = :val1', 
        ExpressionAttributeValues={':val1': 'closed'}
    )

def fetch_open_pifs():
    response = pifTable.scan(FilterExpression=Attr('State').eq('open'))
    if len(response['Items']) > 0:
        return response['Items']
    else:
        return []

def fetch_pif(post_id):
    response = pifTable.query(
            KeyConditionExpression=Key('SubmissionId').eq(post_id)
    )
    if len(response['Items']) > 0:
        return response['Items'][0]
    else:
        return None

def pif_exists(post_id):
    return None is not fetch_pif(post_id)

def update_pif_entries(post_id, pif_entries):
     pifTable.update_item(
        Key={'SubmissionId': post_id},
        UpdateExpression='SET PifEntries = :val1', 
        ExpressionAttributeValues={':val1': pif_entries}
    )
   
    