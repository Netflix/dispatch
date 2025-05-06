import string
import secrets
from typing import List
from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import jwt
from typing import Optional
from pydantic import validator, Field
from pydantic.networks import EmailStr

from sqlalchemy import DateTime, Column, String, LargeBinary, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import TSVectorType

from dispatch.config import (
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_ALG,
    DISPATCH_JWT_EXP,
)
from dispatch.database.core import Base
from dispatch.enums import DispatchEnum, UserRoles
from dispatch.models import OrganizationSlug, PrimaryKey, TimeStampMixin, DispatchBase, Pagination
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
    last_mfa_time = Column(DateTime, nullable=True)
    experimental_features = Column(Boolean, default=False)

    # relationships
    events = relationship("Event", backref="dispatch_user")

    search_vector = Column(
        TSVectorType("email", regconfig="pg_catalog.simple", weights={"email": "A"})
    )

    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches stored hash"""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    def is_owner(self, organization_slug: str) -> bool:
        """Check if user is an owner in the given organization"""
        role = self.get_organization_role(organization_slug)
        return role == UserRoles.owner

    @property
    def token(self):
        now = datetime.utcnow()
        exp = (now + timedelta(seconds=DISPATCH_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    def get_organization_role(self, organization_slug: OrganizationSlug):
        """Gets the user's role for a given organization slug."""
        for o in self.organizations:
            if o.organization.slug == organization_slug:
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
    project = relationship(Project, backref="users", overlaps="dispatch_user_project")

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
    experimental_features: Optional[bool]


class UserUpdate(DispatchBase):
    id: PrimaryKey
    projects: Optional[List[UserProject]]
    organizations: Optional[List[UserOrganization]]
    experimental_features: Optional[bool]
    role: Optional[str] = Field(None, nullable=True)


class UserPasswordUpdate(DispatchBase):
    """Model for password updates only"""
    current_password: str
    new_password: str

    @validator("new_password")
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check for at least one number
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        # Check for at least one uppercase and one lowercase character
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v

    @validator("current_password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Current password is required")
        return v


class AdminPasswordReset(DispatchBase):
    """Model for admin password resets"""
    new_password: str

    @validator("new_password")
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check for at least one number
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        # Check for at least one uppercase and one lowercase character
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v


class UserCreate(DispatchBase):
    email: EmailStr
    password: Optional[str] = Field(None, nullable=True)
    projects: Optional[List[UserProject]]
    organizations: Optional[List[UserOrganization]]
    role: Optional[str] = Field(None, nullable=True)

    @validator("password", pre=True)
    def hash(cls, v):
        return hash_password(str(v))


class UserRegisterResponse(DispatchBase):
    token: Optional[str] = Field(None, nullable=True)


class UserPagination(Pagination):
    items: List[UserRead] = []


class MfaChallengeStatus(DispatchEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class MfaChallenge(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    valid = Column(Boolean, default=False)
    reason = Column(String, nullable=True)
    action = Column(String)
    status = Column(String, default=MfaChallengeStatus.PENDING)
    challenge_id = Column(UUID(as_uuid=True), default=uuid4, unique=True)
    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), nullable=False)
    dispatch_user = relationship(DispatchUser, backref="mfa_challenges")


class MfaPayloadResponse(DispatchBase):
    status: str


class MfaPayload(DispatchBase):
    action: str
    project_id: int
    challenge_id: str
