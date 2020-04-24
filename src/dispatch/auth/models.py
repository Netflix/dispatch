
import string
import secrets
from enum import Enum
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import validator
from sqlalchemy import Column, String, Binary

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase

from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)


def generate_password():
    """Generates a resonable password if none is provided."""

    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(10))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password


def hash_password(password: str):
    """Generates a hashed version of the provided password."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class UserRoles(str, Enum):
    user = "user"
    poweruser = "poweruser"
    admin = "admin"


class DispatchUser(Base, TimeStampMixin):
    email = Column(String, primary_key=True)
    password = Column(Binary, nullable=False)
    role = Column(String, nullable=False, default=UserRoles.user)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def token(self):
        now = datetime.now()
        exp = (now + timedelta(seconds=DISPATCH_JWT_EXP)).timestamp()
        data = {"exp": exp, "email": self.email, "role": self.role}
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    def principals(self):
        return [f"user:{self.email}", f"role:{self.role}"]


class UserBase(DispatchBase):
    email: str

    @validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v

    def principals(self):
        return [f"user:{self.name}"]


class UserLogin(UserBase):
    password: str

    @validator("password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserRegister(UserLogin):
    password: Optional[str]

    @validator("password", pre=True, always=True)
    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(DispatchBase):
    token: Optional[str]


class UserRegisterResponse(DispatchBase):
    email: str
