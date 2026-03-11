import boto3
import logging
from boto3.dynamodb.conditions import Key
import json
from dataclasses import asdict

from botocore.exceptions import ClientError

from shared.dataclasses import ProjectInfo

# https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format


logger = logging.getLogger()
logger.setLevel("INFO")

table = boto3.resource('dynamodb').Table('Portfolio')


def list_projects() -> list[ProjectInfo]:
    try:
        response = table.query(KeyConditionExpression=Key("PK").eq('PJ'))
    except ClientError as e:
        logger.error(e)
        raise
    else:
        return [
            ProjectInfo(item.get('SK')[3:], item.get('Name'), item.get('CategoryId'), item.get('CoverKey'),
                        int(item.get('Year')), item.get('Link'))
            for item in response["Items"]
        ]


def lambda_handler():
    try:
        projects = list_projects()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps([asdict(p) for p in projects])
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

