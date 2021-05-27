import string
import secrets
from typing import List
from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import validator

from sqlalchemy import Column, String, Binary, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import TimeStampMixin, DispatchBase
from dispatch.enums import UserRoles

from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)
from dispatch.project.models import Project, ProjectRead
from dispatch.organization.models import Organization, OrganizationRead


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
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(Binary, nullable=False)

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
            "projects": [UserProject.from_orm(p).dict() for p in self.projects],
            "organizations": [UserOrganization.from_orm(o).dict() for o in self.organizations],
        }
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    def get_project_role(self, project_name):
        """Gets the users role for a given project."""
        for p in self.projects:
            if p.name == project_name:
                return p.role


class DispatchUserOrganization(Base, TimeStampMixin):
    id = Column("id", Integer, primary_key=True)
    dispatch_user_id = Column(Integer, ForeignKey("dispatch_user.id"))
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship(Organization)
    role = Column(String)
    dispatch_user = relationship(DispatchUser, backref="organizations")


class DispatchUserProject(Base, TimeStampMixin):
    id = Column("id", Integer, primary_key=True)
    dispatch_user_id = Column(Integer, ForeignKey("dispatch_user.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship(Project)
    role = Column(String, nullable=False, default=UserRoles.member)
    dispatch_user = relationship(DispatchUser, backref="projects")


class UserProject(DispatchBase):
    project: ProjectRead
    default: Optional[bool] = False
    role: str


class UserOrganization(DispatchBase):
    organization: OrganizationRead
    default: Optional[bool] = False
    role: Optional[str]


class UserBase(DispatchBase):
    email: str
    projects: Optional[List[UserProject]] = []
    organizations: Optional[List[UserOrganization]] = []

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


class UserUpdate(DispatchBase):
    id: int
    password: Optional[str]

    projects: Optional[List[UserProject]]
    organization: Optional[List[UserOrganization]]

    @validator("password", pre=True, always=True)
    def hash(cls, v):
        return hash_password(str(v))


class UserRegisterResponse(DispatchBase):
    token: Optional[str]


class UserPagination(DispatchBase):
    total: int
    items: List[UserRead] = []
