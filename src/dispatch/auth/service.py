"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
import bcrypt

from starlette.requests import Request
from dispatch.plugins.base import plugins
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_JWT_SECRET
)

from cachetools import TTLCache
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from .models import DispatchUser

log = logging.getLogger(__name__)

jwk_key_cache = TTLCache(maxsize=1, ttl=60 * 60)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def get_current_user(*, request: Request):
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        return auth_plugin.get_current_user(request)

    log.warning(
        "No authentication provider has been provided. Default one will be used"
    )
    user_email = from_bearer_token(request)

    if not user_email:
        raise credentials_exception

    return user_email


def from_bearer_token(request: Request):
    """Fetches user from provided bearer token."""
    authorization: str = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return

    token = authorization.split()[1]

    # TODO should we warm this cache up on application start?
    try:
        data = jwt.decode(token, DISPATCH_JWT_SECRET)
    except JWTError:
        return

    return data["email"]


def fetch_user(db_session, email: str):
    return db_session.query(DispatchUser).get(email)


def encode_jwt(user):
    return jwt.encode(user, DISPATCH_JWT_SECRET)


def decode_jwt(user):
    return jwt.decode(user, DISPATCH_JWT_SECRET)


def check_password(passwd: str, hashed: bytes):
    return bcrypt.checkpw(passwd.encode("utf-8"), hashed)


def hash_password(pw: str):
    pw = bytes(pw, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)
