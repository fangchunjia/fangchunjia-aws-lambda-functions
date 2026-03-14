import os
import re
import asyncio

from auth0_api_python import ApiClient, ApiClientOptions
from auth0_api_python.errors import BaseAuthError

AUDIENCE = os.environ.get("AUDIENCE")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")  # e.g. "fangchunjia.eu.auth0.com" (no https://)

# ApiClient handles OIDC discovery and JWKS fetching/caching automatically
_api_client = ApiClient(ApiClientOptions(
    domain=AUTH0_DOMAIN,
    audience=AUDIENCE,
))


def get_policy_document(effect: str, resource: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource,
            }
        ],
    }


def get_token(params: dict) -> str:
    if params.get("type") != "TOKEN":
        raise ValueError('Expected "event.type" parameter to have value "TOKEN"')

    token_string = params.get("authorizationToken")
    if not token_string:
        raise ValueError('Expected "event.authorizationToken" parameter to be set')

    match = re.match(r"^Bearer (.*)$", token_string)
    if not match:
        raise ValueError(
            f'Invalid Authorization token - {token_string} does not match "Bearer .*"'
        )
    return match.group(1)


def authenticate(params: dict) -> dict:
    print(params)
    token = get_token(params)

    # verify_access_token raises BaseAuthError if the token is invalid
    decoded = asyncio.run(_api_client.verify_access_token(token))

    return {
        "principalId": decoded["sub"],
        "policyDocument": get_policy_document("Allow", params["methodArn"]),
        "context": {"scope": decoded.get("scope", "")},
    }


def lambda_handler(event, context):
    try:
        data = authenticate(event)
    except Exception as err:
        print(err)
        raise Exception("Unauthorized")  # API Gateway expects this exact string

    return data