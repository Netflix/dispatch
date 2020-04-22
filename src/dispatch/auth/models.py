from sqlalchemy import Column, String, Binary
from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase
from pydantic import validator


class DispatchUser(Base, TimeStampMixin):
    email = Column(String, primary_key=True)
    password = Column(Binary, nullable=False)


class UserLoginForm(DispatchBase):
    email: str
    password: str

    @validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v

    @validator("password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserLoginResponse(DispatchBase):
    token: str
