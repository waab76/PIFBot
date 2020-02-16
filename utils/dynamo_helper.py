import boto3

from boto3.dynamodb.conditions import Attr, Key

dynamodb = boto3.resource('dynamodb')
pifTable = dynamodb.Table('PIFs')

def pif_exists(post_id):
    return None is not fetch_pif(post_id)
    
def store_pif(submissionId, authorName, pifOptions, expireTime):
    pifTable.put_item(
        Item={
            'SubmissionId': submissionId,
            'Author': authorName,
            'PifOptions': pifOptions,
            'PifEntries': [],
            'State': 'open',
            'ExpireTime': expireTime
        }
    )    

def fetch_pif(post_id):
    response = pifTable.query(
            KeyConditionExpression=Key('SubmissionId').eq(post_id)
    )
    if len(response['Items']) > 0:
        return response['Items'][0]
    else:
        return None

def fetch_open_pifs():
    response = pifTable.scan(FilterExpression=Attr('State').eq('open'))
    return response['Items']