"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from dispatch.plugins.base import plugins
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_AUTHENTICATION_DEFAULT_USER,
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)
from .models import DispatchUser

log = logging.getLogger(__name__)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def get_current_user(*, request: Request):
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        return auth_plugin.get_current_user(request)

    log.debug("No authentication provider. Default one will be used")
    return DISPATCH_AUTHENTICATION_DEFAULT_USER


def gen_token(user):
    user = add_claims(user)
    return jwt.encode(user, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)


def fetch_user(db_session, email: str):
    return db_session.query(DispatchUser).get(email)


def add_claims(user: dict):
    now = datetime.now()
    user["exp"] = (now + timedelta(seconds=DISPATCH_JWT_EXP)).timestamp()
    return user


def check_password(passwd: str, hashed: bytes):
    return bcrypt.checkpw(passwd.encode("utf-8"), hashed)


def hash_password(pw: str):
    pw = bytes(pw, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)
