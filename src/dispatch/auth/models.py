import string
import secrets
from typing import List
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import validator
from sqlalchemy import Column, String, Binary, Integer
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import TimeStampMixin, DispatchBase
from dispatch.enums import UserRoles

from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)


def generate_password():
    """Generates a resonable password if none is provided."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
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


class DispatchUser(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(Binary, nullable=False)
    role = Column(String, nullable=False, default=UserRoles.user)

    search_vector = Column(TSVectorType("email", weights={"email": "A"}))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    @property
    def token(self):
        now = datetime.utcnow()
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


class UserRead(UserBase):
    id: int
    role: str


class UserUpdate(DispatchBase):
    id: int
    role: UserRoles


class UserRegisterResponse(DispatchBase):
    email: str


class UserPagination(DispatchBase):
    total: int
    items: List[UserRead] = []
