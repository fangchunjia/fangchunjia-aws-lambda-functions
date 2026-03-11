import json
import boto3
import logging

table = boto3.resource('dynamodb').Table('Portfolio')

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event):
    try:
        project_id = event['pathParameters']['projectId']
    except KeyError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "error": "Missing projectId"
            })
        }
    body = json.loads(event['body'])
    media_layout = body['mediaLayout']
    
    try:
        table.update_item(
            Key={
                'PK': 'PJ',
                'SK': 'PJ#' + project_id,
            },
            UpdateExpression='set MediaLayout = :l',
            ExpressionAttributeValues={
                ':l': [{"Key": l['key'], "Size": l['size']} for l in media_layout]
            },
            ReturnValues="UPDATED_NEW"
        )
        
        logger.info(f"Successfully updated the media layout of project {project_id}")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                'id': project_id
            })
        }
    except Exception as e:
        logger.error(f"Error updating the project: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            },
            "isBase64Encoded": False,
        }