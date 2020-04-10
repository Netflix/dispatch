from fastapi import APIRouter, Depends, Request
from sqlalchemy import exc
from sqlalchemy.orm import Session
from dispatch.database import get_db

from .models import DispatchUser, UserLoginForm, UserLoginResponse
from .service import fetch_user, encode_jwt, credentials_exception, get_current_user

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse, summary="Login via email, returns a jwt")
def login_user(
    form: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = fetch_user(db_session, form.email)
    if user and user.email == form.email:
        return {"jwt": encode_jwt({"email": user.email})}
    raise credentials_exception


@router.post("/register", response_model=UserLoginResponse, summary="Creates a user, returns jwt")
def register_user(
    user: UserLoginForm,
    db_session: Session = Depends(get_db),
):
    user = DispatchUser(email=user.email)
    db_session.add(user)
    try:
        db_session.commit()
    except exc.IntegrityError:
        # TODO replace exception
        raise credentials_exception

    return {"jwt": encode_jwt({"email": user.email})}


@router.get("/user", response_model=UserLoginResponse, summary="Retrives current user")
def get_user(
    req: Request,
    db_session: Session = Depends(get_db),
):
    return {"jwt": get_current_user(request=req)}
