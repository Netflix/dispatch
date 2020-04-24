"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from fastapi import HTTPException, Depends
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi_permissions import Authenticated, configure_permissions

from sqlalchemy.orm import Session
from dispatch.database import get_db

from dispatch.plugins.base import plugins
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_AUTHENTICATION_DEFAULT_USER,
)
from .models import DispatchUser, UserRegister

log = logging.getLogger(__name__)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def get(*, db_session, email: str):
    return db_session.query(DispatchUser).filter(DispatchUser.email == email).one_or_none()


def create(*, db_session, user_in: UserRegister):
    """Creates a new dispatch user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")
    user = DispatchUser(**user_in.dict(exclude={"password"}), password=password)
    db_session.add(user)
    db_session.commit()
    return user


def get_or_create(*, db_session, user_in: UserRegister):
    """Gets an existing user or creates a new one."""
    user = get(db_session=db_session, email=user_in.email)
    if not user:
        return create(db_session=db_session, user_in=user_in)
    return user


def get_current_user(*, db_session: Session = Depends(get_db), request: Request):
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = DISPATCH_AUTHENTICATION_DEFAULT_USER

    return get_or_create(db_session=db_session, user_in=UserRegister(email=user_email))


def get_active_principals(user: DispatchUser = Depends(get_current_user)):
    """Fetches the current participants for a given user."""
    principals = [Authenticated]
    principals.extend(getattr(user, "principals", []))
    return principals


Permission = configure_permissions(get_active_principals)
