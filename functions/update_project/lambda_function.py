import boto3
import logging
import json

table = boto3.resource('dynamodb').Table('Portfolio')

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
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
    body = json.loads(event['body'])
    name = body.get('name', '')
    category_id = body.get('categoryId', '')
    description = body.get('description', '')
    year = body.get('year', '')
    link = body.get('link', '')

    update_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}
    if name:
        update_expression.append("#N = :n")
        expression_attribute_values[':n'] = name
        expression_attribute_names['#N'] = 'Name'
    if category_id:
        update_expression.append("CategoryId = :c")
        expression_attribute_values[':c'] = category_id
    if description:
        update_expression.append("Description = :d")
        expression_attribute_values[':d'] = description
    if year:
        update_expression.append("#Y = :y")
        expression_attribute_values[':y'] = year
        expression_attribute_names['#Y'] = 'Year'
    if link:
        update_expression.append("Link = :l")
        expression_attribute_values[':l'] = link

    try:
        if expression_attribute_names:
            project = table.update_item(
                Key={
                    'PK': 'PJ',
                    'SK': 'PJ#' + project_id,
                },
                UpdateExpression='set ' + ', '.join(update_expression),
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues="UPDATED_NEW"
            )
        else:
            project = table.update_item(
                Key={
                    'PK': 'PJ',
                    'SK': 'PJ#' + project_id,
                },
                UpdateExpression='set ' + ', '.join(update_expression),
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )
        logger.info(f"Successfully updated the project with ID: {project_id}")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
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
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
        }