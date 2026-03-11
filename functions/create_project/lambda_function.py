import boto3
import logging

table = boto3.resource('dynamodb').Table('Portfolio')

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event):
    # Validate body
    try:
        body = event
        project_id = body['id']
        name = body['name']
        category_id = body['categoryId']
        # description = body['description']
        year = body['year']
        link = body.get('link', '')
    except KeyError as e:
        raise Exception(f"Missing required fields: {e}")

    try:
        table.put_item(
            Item={
                'PK': 'PJ',
                'SK': 'PJ#' + project_id,
                'Name': name,
                'CategoryId': category_id,
                # 'Description': description,
                'Year': year,
                'Link': link,
            }
        )
        logger.info(f"Successfully created project with ID: {project_id}")
        return {
            "id": project_id,
        }
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise