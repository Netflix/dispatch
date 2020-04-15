import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy import exc
from sqlalchemy.orm import Session
from dispatch.database import get_db
from .models import DispatchUser, UserLoginForm, UserLoginResponse
from .service import (
    fetch_user,
    gen_token,
    credentials_exception,
    get_current_user,
    hash_password,
    check_password
)

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse, summary="Login via email, returns a jwt")
def login_user(
    form: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = fetch_user(db_session, form.email)
    if user and check_password(form.password, user.password):
        return {"token": gen_token({"email": user.email})}
    raise credentials_exception


@router.post("/register", response_model=UserLoginResponse, summary="Creates a user, returns jwt")
def register_user(
    user: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = DispatchUser(email=user.email, password=hash_password(user.password))
    db_session.add(user)
    try:
        db_session.commit()
    except exc.IntegrityError as e:
        # User already exists
        logging.warn(e)
        raise credentials_exception

    return {"token": gen_token({"email": user.email})}


@router.get("/user", response_model=UserLoginResponse, summary="Retrives current user")
def get_user(
    req: Request,
    db_session: Session = Depends(get_db),
):
    return {"token": get_current_user(request=req)}
