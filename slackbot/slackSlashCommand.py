import json
import os
import sys
import re
import base64
import boto3
from botocore.exceptions import ClientError

''' Who's Out Calls BambooHR's API to find out Who's Out Of Office,
    Group and Filter on employee information such as location or department.
    Results are returned matching the current date that the code is run.
'''

def lambda_handler(event, context):
    ''' Receive event and context from API Gateway
        Send the body from Slack to the main function to decide what to do next
        Just return a quick response to let Slack know we are working on it.
    '''
    stage = os.environ["stage"]
    lambdac = boto3.client('lambda')
    
    response = lambdac.invoke(
        FunctionName='whosout-'+stage+'-slackSlashCommandReturn',
        InvocationType='Event',
        Payload=json.dumps(event)
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': ':thinking_face: Let\'s see who is out of the office today...')
    }
