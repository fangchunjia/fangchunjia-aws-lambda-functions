import boto3
import logging
import json
from dataclasses import asdict

from shared.dataclasses import About

# https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format


logger = logging.getLogger()
logger.setLevel("INFO")

table = boto3.resource('dynamodb').Table('Portfolio')


class AboutNotFoundError(Exception):
    """Raised when the project cannot be found"""


def get_about() -> About:
    try:
        response = table.get_item(
            Key={
                'PK': 'ABT',
                'SK': 'ABT',
            },
        )
        about = response['Item']
        return About(about.get('Text'))
    except KeyError:
        raise AboutNotFoundError()


def lambda_handler(event, context):
    try:
        about = get_about()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps(asdict(about))
        }
    except AboutNotFoundError:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "error": "Error getting about"
            })
        }
    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "error": "Internal server error"
            })
        }


