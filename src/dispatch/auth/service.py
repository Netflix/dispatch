"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List, Optional
from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
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
from .models import DispatchUser, UserRegister, UserUpdate

log = logging.getLogger(__name__)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def get(*, db_session, user_id: int) -> Optional[DispatchUser]:
    """Returns an user based on the given user id."""
    return db_session.query(DispatchUser).filter(DispatchUser.id == user_id).one_or_none()


def get_by_email(*, db_session, email: str) -> Optional[DispatchUser]:
    """Returns an user object based on user email."""
    return db_session.query(DispatchUser).filter(DispatchUser.email == email).one_or_none()


def create(*, db_session, user_in: UserRegister) -> DispatchUser:
    """Creates a new dispatch user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")
    user = DispatchUser(**user_in.dict(exclude={"password"}), password=password)
    db_session.add(user)
    db_session.commit()
    return user


def get_or_create(*, db_session, user_in: UserRegister) -> DispatchUser:
    """Gets an existing user or creates a new one."""
    user = get_by_email(db_session=db_session, email=user_in.email)
    if not user:
        return create(db_session=db_session, user_in=user_in)
    return user


def update(*, db_session, user: DispatchUser, user_in: UserUpdate) -> DispatchUser:
    """Updates a user."""
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    db_session.add(user)
    db_session.commit()
    return user


def get_current_user(*, db_session: Session = Depends(get_db), request: Request) -> DispatchUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = DISPATCH_AUTHENTICATION_DEFAULT_USER

    if not user_email:
        log.exception(
            f"Unable to determine user email based on configured auth provider or no default auth user email defined. Provider: {DISPATCH_AUTHENTICATION_PROVIDER_SLUG}"
        )

    return get_or_create(db_session=db_session, user_in=UserRegister(email=user_email))


def get_active_principals(user: DispatchUser = Depends(get_current_user)) -> List[str]:
    """Fetches the current participants for a given user."""
    principals = [Authenticated]
    principals.extend(getattr(user, "principals", []))
    return principals


Permission = configure_permissions(get_active_principals)
