import boto3

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
pifTable = dynamodb.Table('PIFs')

def pifExists(post_id):
    response = pifTable.query(
            KeyConditionExpression=Key('SubmissionId').eq(post_id)
    )
    if len(response['Items']) < 1:
        print('PIF not found')
        return False
    else:
        return True
    
def storePIF(submissionId, authorName, pifType):
    pifTable.put_item(
        Item={
            'SubmissionId': submissionId,
            'Author': authorName,
            'PIFType': pifType
        }
    )