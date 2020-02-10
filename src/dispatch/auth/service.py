import requests
from cachetools import TTLCache
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from dispatch.config import JWKS_URL

jwk_key_cache = TTLCache(maxsize=1, ttl=60 * 60)


def get_current_user(*, request: Request):
    """Gets the current user based on the token."""
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )
    authorization: str = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise credentials_exception

    token = authorization.split()[1]

    # TODO should we warm this cache up on application start?
    try:
        key = jwk_key_cache[JWKS_URL]
    except Exception:
        key = requests.get(JWKS_URL).json()["keys"][0]
        jwk_key_cache[JWKS_URL] = key

    try:
        data = jwt.decode(token, key)
    except JWTError:
        raise credentials_exception

    return data["email"]
