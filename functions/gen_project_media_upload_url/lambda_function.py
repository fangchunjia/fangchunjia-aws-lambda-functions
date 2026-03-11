import json
import boto3
from botocore.exceptions import ClientError


def gen_presigned_url(project_id: str, key: str):
    """
    Reference: https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html
    """
    # Create S3 client with explicit region configuration
    s3_client = boto3.client("s3", region_name='eu-west-3')

    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": 'fangchunjia',
                "Key": key,
            },
            ExpiresIn=600  # seconds
        )
    except ClientError:
        print(f"Couldn't get a presigned URL for client method.")
        raise
    return url


def lambda_handler(event):
    try:
        # print(event)
        try:
            path_params = event['pathParameters']
            query_params = event['queryStringParameters']
            project_id = path_params['projectId']
            filename = query_params['filename']
        except ValueError:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "isBase64Encoded": False,
                "body": json.dumps({
                    "error": 'Missing projectId or filename',
                })
            }

        key = f'projects/{project_id}/{filename}'

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "isBase64Encoded": False,
            "body": json.dumps({
                "uploadUrl": gen_presigned_url(project_id, key),
                "key": filename
            })
        }
    except Exception as e:
        print(e)
        raise Exception(f"Error: {e}")

