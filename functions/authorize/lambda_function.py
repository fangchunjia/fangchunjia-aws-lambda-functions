import os
import re

from auth0.authentication.token_verifier import (
    TokenVerifier,
    AsymmetricSignatureVerifier,
)

# Reference: https://auth0.com/docs/customize/integrations/aws/aws-api-gateway-custom-authorizers

AUDIENCE = os.environ.get("AUDIENCE")
TOKEN_ISSUER = os.environ.get("TOKEN_ISSUER")
JWKS_URI = os.environ.get("JWKS_URI")

# AsymmetricSignatureVerifier fetches and caches JWKS automatically
_signature_verifier = AsymmetricSignatureVerifier(JWKS_URI)
_token_verifier = TokenVerifier(
    signature_verifier=_signature_verifier,
    issuer=TOKEN_ISSUER,
    audience=AUDIENCE,
)


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

    # verify() raises TokenValidationError if the token is invalid,
    # and returns the decoded payload if valid
    decoded = _token_verifier.verify(token)

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
