import os
import re
import requests

from authlib.jose import JsonWebToken
from authlib.jose.errors import JoseError

AUDIENCE = os.environ.get("AUDIENCE")
TOKEN_ISSUER = os.environ.get("TOKEN_ISSUER")
JWKS_URI = os.environ.get("JWKS_URI")

# Restrict to RS256 only — prevents algorithm confusion attacks
_jwt = JsonWebToken(["RS256"])

# Cache JWKS at module level so it's reused across warm Lambda invocations
_jwks = None

def get_jwks() -> dict:
    global _jwks
    if _jwks is None:
        _jwks = requests.get(JWKS_URI).json()
    return _jwks


_claims_options = {
    "iss": {"essential": True, "value": TOKEN_ISSUER},
    "aud": {"essential": True, "value": AUDIENCE},
}


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

    # decode() verifies the signature using the matching key from JWKS,
    # then validate() checks iss, aud, exp, nbf
    claims = _jwt.decode(token, get_jwks(), claims_options=_claims_options)
    claims.validate()

    return {
        "principalId": claims["sub"],
        "policyDocument": get_policy_document("Allow", params["methodArn"]),
        "context": {"scope": claims.get("scope", "")},
    }


def lambda_handler(event, context):
    try:
        data = authenticate(event)
    except Exception as err:
        print(err)
        raise Exception("Unauthorized")  # API Gateway expects this exact string

    return data