from typing import Optional
from datetime import datetime, timedelta

import validators

from pydantic.fields import Field
from pydantic.networks import EmailStr
from pydantic import BaseModel, validator
from pydantic.types import conint, constr, SecretStr

from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey

# pydantic type that limits the range of primary keys
PrimaryKey = conint(gt=0, lt=2147483647)
NameStr = constr(regex=r"^(?!\s*$).+", strip_whitespace=True, min_length=3)
OrganizationSlug = constr(regex=r"^[\w]+(?:_[\w]+)*$", min_length=3)


# SQLAlchemy models...
class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):  # noqa
        return relationship("Project")


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class ContactMixin(TimeStampMixin):
    """Contact mixin"""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)


class EvergreenMixin(object):
    """Evergreen mixin."""

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime, default=datetime.utcnow())

    @hybrid_property
    def overdue(self):
        now = datetime.utcnow()
        next_reminder = self.evergreen_last_reminder_at + timedelta(
            days=self.evergreen_reminder_interval
        )

        if now >= next_reminder:
            return True

    @overdue.expression
    def overdue(cls):
        return (
            func.date_part("day", func.now() - cls.evergreen_last_reminder_at)
            >= cls.evergreen_reminder_interval
        )


# @listens_for(EvergreenMixin.evergreen, "set", propagate=True)
def reset_last_reminded(target, value, oldvalue, initiator):
    """Reset last reminder at if evergreen goes from disabled -> enabled."""
    if not oldvalue:
        target.evergreen_last_reminder_at = datetime.utcnow()
    target.evergreen = value


# Pydantic models...
class DispatchBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True

        json_encoders = {
            # custom output conversion for datetime
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class EvergreenBase(DispatchBase):
    evergreen: Optional[bool] = False
    evergreen_owner: Optional[EmailStr]
    evergreen_reminder_interval: Optional[int] = 90
    evergreen_last_reminder_at: Optional[datetime] = Field(None, nullable=True)


class ResourceBase(DispatchBase):
    resource_type: Optional[str] = Field(None, nullable=True)
    resource_id: Optional[str] = Field(None, nullable=True)
    weblink: Optional[str] = Field(None, nullable=True)

    @validator("weblink")
    def sanitize_weblink(cls, v):
        if v:
            if not validators.url(v):
                raise ValueError("Weblink must be a valid url.")
        return v


class ContactBase(DispatchBase):
    email: EmailStr
    name: Optional[str] = Field(None, nullable=True)
    is_active: Optional[bool] = True
    is_external: Optional[bool] = False
    company: Optional[str] = Field(None, nullable=True)
    contact_type: Optional[str] = Field(None, nullable=True)
    notes: Optional[str] = Field(None, nullable=True)
    owner: Optional[str] = Field(None, nullable=True)
