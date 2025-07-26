import os
import requests
from fastapi import Request, HTTPException
from jose import jwt, JWTError

STACK_PROJECT_ID = os.environ["STACK_PROJECT_ID"]
JWKS_URL = f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}/.well-known/jwks.json"

_jwks = None


def get_jwks():
    global _jwks
    if _jwks is None:
        resp = requests.get(JWKS_URL)
        resp.raise_for_status()
        _jwks = resp.json()
    return _jwks


async def validate_stack_auth_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = auth_header.split(" ")[1]
    jwks = get_jwks()
    try:
        header = jwt.get_unverified_header(token)
        for jwk in jwks["keys"]:
            if jwk["kid"] == header["kid"]:
                payload = jwt.decode(
                    token, jwk, algorithms=["ES256", "RS256"], audience=STACK_PROJECT_ID
                )
                return payload  # payload['sub'] is the user ID
        raise HTTPException(status_code=401, detail="Invalid token: key not found")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
