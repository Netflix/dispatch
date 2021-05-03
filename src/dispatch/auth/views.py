from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from dispatch.auth.permissions import OrganizationOwnerPermission, PermissionsDependency

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import (
    UserLogin,
    UserRegister,
    UserRead,
    UserUpdate,
    UserPagination,
    UserLoginResponse,
    UserRegisterResponse,
)
from .service import get, get_by_email, update, create, get_current_user


auth_router = APIRouter()
user_router = APIRouter()


@user_router.get("", response_model=UserPagination)
def get_users(*, common: dict = Depends(common_parameters)):
    """
    Get all users.
    """
    return search_filter_sort_paginate(model="DispatchUser", **common)


@user_router.get("/{user_id}", response_model=UserRead)
def get_user(*, db_session: Session = Depends(get_db), user_id: int):
    """
    Get a user.
    """
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="The user with this id does not exist.")
    return user


@auth_router.get("/me", response_model=UserRead)
def get_me(
    req: Request,
    db_session: Session = Depends(get_db),
):
    return get_current_user(db_session=db_session, request=req)


@user_router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def update_user(
    *,
    db_session: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
):
    """
    Update a user.
    """
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="The user with this id does not exist.")

    user = update(db_session=db_session, user=user, user_in=user_in)

    return user


@auth_router.post("/login", response_model=UserLoginResponse)
def login_user(
    user_in: UserLogin,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user and user.check_password(user_in.password):
        return {"token": user.token}
    raise HTTPException(status_code=400, detail="Invalid username or password")


@auth_router.post("/register", response_model=UserRegisterResponse)
def register_user(
    user_in: UserRegister,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if not user:
        user = create(db_session=db_session, user_in=user_in)
    else:
        raise HTTPException(status_code=400, detail="User with that email address exists.")

    return user
