#import json

''' Save the day with some help text
'''
def lambda_handler(event, context):
    ''' We already know the user needs help
        So nothing to parse here...
        For now?
    '''
    help_output = "Please contact support."
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': help_output
    }