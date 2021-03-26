from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.auth.permissions import AdminPermission, PermissionsDependency

from dispatch.database.core import get_db
from dispatch.database.service import search_filter_sort_paginate

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


@user_router.get("/", response_model=UserPagination)
def get_users(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all users.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="DispatchUser",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@user_router.get("/{user_id}", response_model=UserRead)
def get_user(*, db_session: Session = Depends(get_db), user_id: int):
    """
    Get a user.
    """
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="The user with this id does not exist.")
    return user


@user_router.put(
    "/{user_id}",
    response_model=UserUpdate,
    dependencies=[Depends(PermissionsDependency([AdminPermission]))],
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


@user_router.get("/me", response_model=UserRead)
def get_me(
    req: Request,
    db_session: Session = Depends(get_db),
):
    return get_current_user(db_session=db_session, request=req)
