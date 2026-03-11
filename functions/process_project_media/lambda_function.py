import json
import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from urllib.parse import unquote_plus
from pathlib import PurePosixPath
import logging

from shared.dataclasses import MediaMetadata

logger = logging.getLogger()
logger.setLevel("INFO")


def get_object_metadata(key: str) -> MediaMetadata:
    try:
        s3_client = boto3.client("s3", region_name='eu-west-3')
        decoded_key = unquote_plus(key)
        response = s3_client.head_object(Bucket='fangchunjia', Key=decoded_key)
        metadata = response['Metadata']
        # seq = metadata.get('seq')
        # size = metadata.get('size')
        return MediaMetadata(key=key)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print("Object not found")
        else:
            raise


def get_project_id_from_key(key: str) -> str:
    path = PurePosixPath(key)
    project_id = path.parts[1]
    return project_id


def get_media_filename(key: str) -> str:
    path = PurePosixPath(key)
    filename = path.parts[2]
    return filename


def create_media_metadata(media_metadata: MediaMetadata):
    project_id = get_project_id_from_key(media_metadata.key)
    media_filename = get_media_filename(media_metadata.key)
    table = boto3.resource('dynamodb').Table('Portfolio')

    try:
        metadata = table.put_item(
            Item={
                'PK': 'PJ#' + project_id,
                'SK': 'FL#' + media_filename,
                'Key': media_metadata.key,
                # 'Seq': media_metadata.seq,
                # 'Size': media_metadata.size,
            }
        )
        logger.info(f"Successfully created media metadata for media {media_metadata.key}")
        return
    except Exception as e:
        logger.error(f"Error creating media metadata: {str(e)}")
        raise

def lambda_handler(event, context):
    try:
        print(event)
        print(event['Records'])
        record_bodies = [json.loads(records['body']) for records in event['Records']]
        object_keys = [body['Records'][0]['s3']['object']['key'] for body in record_bodies]
        for object_key in object_keys:
            media_metadata = get_object_metadata(object_key)
            create_media_metadata(media_metadata)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
    return
