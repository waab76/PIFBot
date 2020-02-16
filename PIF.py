import boto3
import json
import praw

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def buildPIF(submission, pifbotCommand):
    parts = pifbotCommand.split()
    if parts[1] == "lottery":
        return Lottery(submission.author.name, submission.id, parts[2])
    elif parts[1] == "range":
        return Range(submission.author.name, submission.id, parts[2])
    elif parts[1] == "poker":
        return Poker(submission.author.name, submission.id, parts[2])

class PIF:
    def __init__(self, creator, post_id, duration):
        self.creator = creator
        self.post_id = post_id
        self.duration = duration
        self.pifTable = dynamodb.Table('PIFs')

    def printCreator(self):
        print(self.creator)

    def initialize(self):
        print("PIF type not implemented")

class Lottery(PIF):
    def __init__(self, creator, post_id, duration):
        super().__init__(creator, post_id, duration)

    def initialize(self):
        table = dynamodb.Table('PIFs')
        response = table.query(
            KeyConditionExpression=Key('SubmissionId').eq(self.post_id)
        )   

        if len(response['Items']) < 1:
            print('PIF not found')
            table.put_item(
                Item={
                    'SubmissionId': self.post_id,
                    'Author': self.creator,
                    'Duration': self.duration
                }
            )
            
        else:
            print('PIF found')
            print(response['Items'][0])
             

class Range(PIF):
    pass

class Poker(PIF):
    pass
