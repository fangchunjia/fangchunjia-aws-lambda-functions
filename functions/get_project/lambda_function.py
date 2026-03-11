import boto3
import logging
from boto3.dynamodb.conditions import Key
import json
from dataclasses import dataclass, asdict

from shared.dataclasses import Project, ProjectMediaLayoutItem

# https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format


logger = logging.getLogger()
logger.setLevel("INFO")

table = boto3.resource('dynamodb').Table('Portfolio')


class ProjectNotFoundError(Exception):
    """Raised when the project cannot be found"""


def list_project_medias_s3(project_id: str) -> list[str]:
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket='fangchunjia', Prefix=f'projects/{project_id}/')
    return [{'Key': item['Key']} for item in response['Contents']]


def get_project(project_id: str) -> Project:
    try:
        response = table.get_item(
            Key={
                'PK': 'PJ',
                'SK': f'PJ#{project_id}'
            },
        )
        project = response['Item']
    except KeyError:
        raise ProjectNotFoundError()
    if project.get('MediaLayout', None) is None:
        project['MediaLayout'] = list_project_medias_s3(project_id)
    try:
        # print(project.get('MediaLayout', []))
        # Casting year to int due to https://github.com/boto/boto3/issues/369#issuecomment-157205696
        return Project(
            project_id,
            project.get('Name'),
            project.get('Description'),
            project.get('CategoryId'),
            project.get('CoverKey'),
            int(project.get('Year')),
            project.get('Link'),
            [
                ProjectMediaLayoutItem(l.get('Key'), l.get('Size', 'm'))
                for l in project.get('MediaLayout', [])
            ],
        )
    except Exception as e:
        logger.error(e)
        raise Exception(f"An error occurred when getting the project: {e}")


def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        project_id = event['pathParameters']['projectId']
    except KeyError as e:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "error": "Missing projectId"
            })
        }
    try:
        project = get_project(project_id)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps(asdict(project))
        }
    except ProjectNotFoundError:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "error": "Project not found"
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

