import string
import secrets
from typing import List
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import validator, Field
from pydantic.networks import EmailStr

from sqlalchemy import Column, String, LargeBinary, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import TSVectorType

from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)
from dispatch.database.core import Base
from dispatch.enums import UserRoles
from dispatch.models import PrimaryKey
from dispatch.models import TimeStampMixin, DispatchBase
from dispatch.organization.models import Organization, OrganizationRead
from dispatch.project.models import Project, ProjectRead


def generate_password():
    """Generates a reasonable password if none is provided."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)  # noqa
            and sum(c.isdigit() for c in password) >= 3  # noqa
        ):
            break
    return password


def hash_password(password: str):
    """Generates a hashed version of the provided password."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class DispatchUser(Base, TimeStampMixin):
    __table_args__ = {"schema": "dispatch_core"}

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(LargeBinary, nullable=False)

    search_vector = Column(TSVectorType("email", weights={"email": "A"}))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    @property
    def token(self):
        now = datetime.utcnow()
        exp = (now + timedelta(seconds=DISPATCH_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    def get_organization_role(self, organization_name):
        """Gets the users role for a given organization."""
        for o in self.organizations:
            if o.organization.name == organization_name:
                return o.role


class DispatchUserOrganization(Base, TimeStampMixin):
    __table_args__ = {"schema": "dispatch_core"}
    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), primary_key=True)
    dispatch_user = relationship(DispatchUser, backref="organizations")

    organization_id = Column(Integer, ForeignKey(Organization.id), primary_key=True)
    organization = relationship(Organization, backref="users")

    role = Column(String, default=UserRoles.member)


class DispatchUserProject(Base, TimeStampMixin):
    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), primary_key=True)
    dispatch_user = relationship(DispatchUser, backref="projects")

    project_id = Column(Integer, ForeignKey(Project.id), primary_key=True)
    project = relationship(Project, backref="users")

    default = Column(Boolean, default=False)

    role = Column(String, nullable=False, default=UserRoles.member)


class UserProject(DispatchBase):
    project: ProjectRead
    default: Optional[bool] = False
    role: Optional[str] = Field(None, nullable=True)


class UserOrganization(DispatchBase):
    organization: OrganizationRead
    default: Optional[bool] = False
    role: Optional[str] = Field(None, nullable=True)


class UserBase(DispatchBase):
    email: EmailStr
    projects: Optional[List[UserProject]] = []

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
    password: Optional[str] = Field(None, nullable=True)

    @validator("password", pre=True, always=True)
    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(DispatchBase):
    projects: Optional[List[UserProject]]
    token: Optional[str] = Field(None, nullable=True)


class UserRead(UserBase):
    id: PrimaryKey
    role: Optional[str] = Field(None, nullable=True)


class UserUpdate(DispatchBase):
    id: PrimaryKey
    password: Optional[str] = Field(None, nullable=True)
    projects: Optional[List[UserProject]]
    organizations: Optional[List[UserOrganization]]
    role: Optional[str] = Field(None, nullable=True)

    @validator("password", pre=True)
    def hash(cls, v):
        return hash_password(str(v))


class UserRegisterResponse(DispatchBase):
    token: Optional[str] = Field(None, nullable=True)


class UserPagination(DispatchBase):
    total: int
    items: List[UserRead] = []
