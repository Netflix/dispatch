"""This module defines the models for the Dispatch authentication system."""

import string
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import jwt
from pydantic import field_validator
from pydantic import EmailStr

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
    """Generate a random, strong password with at least one lowercase, one uppercase, and three digits."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        # Ensure password meets complexity requirements
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password


def hash_password(password: str):
    """Hash a password using bcrypt."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class DispatchUser(Base, TimeStampMixin):
    """SQLAlchemy model for a Dispatch user."""

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
        """Check if the provided password matches the stored hash."""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password for the user."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    def is_owner(self, organization_slug: str) -> bool:
        """Return True if the user is an owner in the given organization."""
        role = self.get_organization_role(organization_slug)
        return role == UserRoles.owner

    @property
    def token(self):
        """Generate a JWT token for the user."""
        now = datetime.utcnow()
        exp = (now + timedelta(seconds=DISPATCH_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, DISPATCH_JWT_SECRET, algorithm=DISPATCH_JWT_ALG)

    def get_organization_role(self, organization_slug: OrganizationSlug):
        """Get the user's role for a given organization slug."""
        for o in self.organizations:
            if o.organization.slug == organization_slug:
                return o.role


class DispatchUserOrganization(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and organizations."""

    __table_args__ = {"schema": "dispatch_core"}
    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), primary_key=True)
    dispatch_user = relationship(DispatchUser, backref="organizations")

    organization_id = Column(Integer, ForeignKey(Organization.id), primary_key=True)
    organization = relationship(Organization, backref="users")

    role = Column(String, default=UserRoles.member)


class DispatchUserProject(Base, TimeStampMixin):
    """SQLAlchemy model for the relationship between users and projects."""

    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), primary_key=True)
    dispatch_user = relationship(DispatchUser, backref="projects")

    project_id = Column(Integer, ForeignKey(Project.id), primary_key=True)
    project = relationship(Project, backref="users", overlaps="dispatch_user_project")

    default = Column(Boolean, default=False)

    role = Column(String, nullable=False, default=UserRoles.member)


class UserProject(DispatchBase):
    """Pydantic model for a user's project membership."""

    project: ProjectRead
    default: bool | None = False
    role: str | None = None


class UserOrganization(DispatchBase):
    """Pydantic model for a user's organization membership."""

    organization: OrganizationRead
    default: bool | None = False
    role: str | None = None


class UserBase(DispatchBase):
    """Base Pydantic model for user data."""

    email: EmailStr
    projects: list[UserProject] | None = []
    organizations: list[UserOrganization] | None = []

    @field_validator("email")
    @classmethod
    def email_required(cls, v):
        """Ensure the email field is not empty."""
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v


class UserLogin(UserBase):
    """Pydantic model for user login data."""

    password: str | None = None

    @field_validator("password")
    @classmethod
    def password_required(cls, v):
        """Ensure the password field is not empty."""
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserRegister(UserLogin):
    """Pydantic model for user registration data."""

    password: str | None = None

    @field_validator("password", mode="before")
    @classmethod
    def password_required(cls, v):
        """Generate and hash a password if not provided."""
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(DispatchBase):
    """Pydantic model for the response after user login."""

    projects: list[UserProject] | None
    token: str | None = None


class UserRead(UserBase):
    """Pydantic model for reading user data."""

    id: PrimaryKey
    role: str | None = None
    experimental_features: bool | None = None


class UserUpdate(DispatchBase):
    """Pydantic model for updating user data."""

    id: PrimaryKey
    projects: list[UserProject] | None = None
    organizations: list[UserOrganization] | None
    experimental_features: bool | None = None
    role: str | None = None


class UserPasswordUpdate(DispatchBase):
    """Pydantic model for password updates only."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate the new password for length and complexity."""
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v

    @field_validator("current_password")
    @classmethod
    def password_required(cls, v):
        """Ensure the current password is provided."""
        if not v:
            raise ValueError("Current password is required")
        return v


class AdminPasswordReset(DispatchBase):
    """Pydantic model for admin password resets."""

    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate the new password for length and complexity."""
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v


class UserCreate(DispatchBase):
    """Pydantic model for creating a new user."""

    email: EmailStr
    password: str | None = None
    projects: list[UserProject] | None = None
    organizations: list[UserOrganization] | None = None
    role: str | None = None

    @field_validator("password", mode="before")
    @classmethod
    def hash(cls, v):
        """Hash the password before storing."""
        return hash_password(str(v))


class UserRegisterResponse(DispatchBase):
    """Pydantic model for the response after user registration."""

    token: str | None = None


class UserPagination(Pagination):
    """Pydantic model for paginated user results."""

    items: list[UserRead] = []


class MfaChallengeStatus(DispatchEnum):
    """Enumeration of possible MFA challenge statuses."""

    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    PENDING = "pending"


class MfaChallenge(Base, TimeStampMixin):
    """SQLAlchemy model for an MFA challenge event."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    valid = Column(Boolean, default=False)
    reason = Column(String, nullable=True)
    action = Column(String)
    status = Column(String, default=MfaChallengeStatus.PENDING)
    challenge_id = Column(UUID(as_uuid=True), default=uuid4, unique=True)
    dispatch_user_id = Column(Integer, ForeignKey(DispatchUser.id), nullable=False)
    dispatch_user = relationship(DispatchUser, backref="mfa_challenges")


class MfaPayloadResponse(DispatchBase):
    """Pydantic model for the response to an MFA challenge payload."""

    status: str


class MfaPayload(DispatchBase):
    """Pydantic model for an MFA challenge payload."""

    action: str
    project_id: int
    challenge_id: str
