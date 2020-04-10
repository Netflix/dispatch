from sqlalchemy import (
    Column,
    String)
from dispatch.database import Base
from dispatch.models import  TimeStampMixin,DispatchBase
from pydantic import validator

class DispatchUser(Base, TimeStampMixin):
    email = Column(String, primary_key=True)

class UserLoginForm(DispatchBase):
    email: str

    @validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v

class UserLoginResponse(DispatchBase):
    jwt: str
