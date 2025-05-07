"""Shared models and mixins for the Dispatch application."""

from datetime import datetime, timedelta, timezone
from typing import ClassVar
from typing_extensions import Annotated

from pydantic import EmailStr
from pydantic import Field, StringConstraints, ConfigDict, BaseModel
from pydantic import SecretStr

from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

# pydantic type that limits the range of primary keys
PrimaryKey = Annotated[int, Field(gt=0, lt=2147483647)]
NameStr = Annotated[str, StringConstraints(pattern=r".*\S.*", strip_whitespace=True, min_length=3)]
OrganizationSlug = Annotated[str, StringConstraints(pattern=r"^[\w]+(?:_[\w]+)*$", min_length=3)]


# SQLAlchemy models...
class ProjectMixin(object):
    """Project mixin for adding project relationships to models."""

    @declared_attr
    def project_id(cls):  # noqa
        """Returns the project_id column."""
        return Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):
        """Returns the project relationship."""
        return relationship("Project")


class TimeStampMixin(object):
    """Timestamping mixin for created_at and updated_at fields."""

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        """Updates the updated_at field to the current UTC time."""
        target.updated_at = datetime.now(timezone.utc)

    @classmethod
    def __declare_last__(cls):
        """Registers the before_update event to update the updated_at field."""
        event.listen(cls, "before_update", cls._updated_at)


class ContactMixin(TimeStampMixin):
    """Contact mixin for contact-related fields."""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin for resource-related fields."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)


class EvergreenMixin(object):
    """Evergreen mixin for evergreen-related fields and logic."""

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @hybrid_property
    def overdue(self):
        """Returns True if the evergreen reminder is overdue."""
        now = datetime.now(timezone.utc)
        if self.evergreen_last_reminder_at is not None and self.evergreen_reminder_interval is not None:
            next_reminder = self.evergreen_last_reminder_at + timedelta(
                days=self.evergreen_reminder_interval
            )
            if now >= next_reminder:
                return True
        return False

    @overdue.expression
    def overdue(cls):
        """SQL expression for checking if the evergreen reminder is overdue."""
        return (
            func.date_part("day", func.now() - cls.evergreen_last_reminder_at)
            >= cls.evergreen_reminder_interval  # noqa
        )


class FeedbackMixin(object):
    """Feedback mixin for feedback-related fields."""

    rating = Column(String)
    feedback = Column(String)


# Pydantic models...
class DispatchBase(BaseModel):
    """Base Pydantic model with shared config for Dispatch models."""
    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        json_encoders={
            # custom output conversion for datetime
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if v else None,
            SecretStr: lambda v: v.get_secret_value() if v else None,
        },
    )


class Pagination(DispatchBase):
    """Pydantic model for paginated results."""
    itemsPerPage: int
    page: int
    total: int


class PrimaryKeyModel(BaseModel):
    """Pydantic model for a primary key field."""
    id: PrimaryKey


class EvergreenBase(DispatchBase):
    """Base Pydantic model for evergreen resources."""
    evergreen: bool | None = False
    evergreen_owner: EmailStr | None = None
    evergreen_reminder_interval: int | None = 90
    evergreen_last_reminder_at: datetime | None = None


class ResourceBase(DispatchBase):
    """Base Pydantic model for resource-related fields."""
    resource_type: str | None = None
    resource_id: str | None = None
    weblink: str | None = None


class ContactBase(DispatchBase):
    """Base Pydantic model for contact-related fields."""
    email: EmailStr
    name: str | None = None
    is_active: bool | None = True
    is_external: bool | None = False
    company: str | None = None
    contact_type: str | None = None
    notes: str | None = None
    owner: str | None = None
