import boto3
import logging
import json

table = boto3.resource('dynamodb').Table('Portfolio')

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
    body = json.loads(event['body'])
    text = body.get('text', '')

    try:
        about = table.update_item(
                Key={
                    'PK': 'ABT',
                    'SK': 'ABT',
                },
                UpdateExpression='set #T = :t',
                ExpressionAttributeValues={
                    ':t': text
                },
                ExpressionAttributeNames={
                    '#T': 'Text'
                },
                ReturnValues="UPDATED_NEW"
            )
        logger.info(f"Successfully updated about")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            },
            "isBase64Encoded": False,
        }
    except Exception as e:
        logger.error(f"Error updating about: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            },
            "isBase64Encoded": False,
        }