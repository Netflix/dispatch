from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import exc
from sqlalchemy.orm import Session

from dispatch.auth.service import get_current_user
from dispatch.database import get_db, search_filter_sort_paginate


from .models import DispatchUser, UserLoginForm, UserLoginResponse
from .service import fetch_user, encode_jwt, credentials_exception

router = APIRouter()

@router.post("/login", response_model=UserLoginResponse, summary="Login via email, returns a jwt")
def login_user(
    user: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = fetch_user(db_session, user.email)
    if user:
        return {"jwt":encode_jwt({"email":user.email})}
    raise credentials_exception


@router.post("/register", response_model=UserLoginResponse, summary="Login via email, returns a jwt")
def register_user(
    user: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = DispatchUser(email=user.email)
    db_session.add(user)
    try:
        db_session.commit()
    except exc.IntegrityError:
        ## TODO replace exception
        raise credentials_exception

    return {"jwt":encode_jwt({"email":user.email})}
