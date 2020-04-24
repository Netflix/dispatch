from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from dispatch.database import get_db
from .models import UserLogin, UserRegister, UserLoginResponse, UserRegisterResponse
from .service import (
    get,
    create,
    get_current_user,
)

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse, summary="Login a user")
def login_user(
    user_in: UserLogin, db_session: Session = Depends(get_db),
):
    user = get(db_session=db_session, email=user_in.email)
    if user and user.check_password:
        return {"token": user.token}
    raise HTTPException(status_code=400, detail="Invalid username or password")


@router.post("/register", response_model=UserRegisterResponse, summary="Registers a new user.")
def register_user(
    user_in: UserRegister, db_session: Session = Depends(get_db),
):
    user = get(db_session=db_session, email=user_in.email)
    if not user:
        user = create(db_session=db_session, user_in=user_in)
    else:
        raise HTTPException(status_code=400, detail="User with that email address exists.")

    return user


@router.get("/user", response_model=UserLoginResponse, summary="Returns current user")
def get_user(
    req: Request, db_session: Session = Depends(get_db),
):
    return {"token": get_current_user(request=req)}
