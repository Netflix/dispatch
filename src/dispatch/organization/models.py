"""Models for organization resources in the Dispatch application."""

from slugify import slugify

from sqlalchemy.event import listen
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, OrganizationSlug, PrimaryKey, Pagination


class Organization(Base):
    """SQLAlchemy model for organization resources."""
    __table_args__ = {"schema": "dispatch_core"}

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    slug = Column(String)
    default = Column(Boolean)
    description = Column(String)
    banner_enabled = Column(Boolean)
    banner_color = Column(String)
    banner_text = Column(String)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


def generate_slug(target, value, oldvalue, initiator):
    """Creates a reasonable slug based on organization name."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value, separator="_")


listen(Organization.name, "set", generate_slug)


class OrganizationBase(DispatchBase):
    """Base Pydantic model for organization resources."""
    id: PrimaryKey | None = None
    name: NameStr
    description: str | None = None
    default: bool | None = False
    banner_enabled: bool | None = False
    banner_color: str | None = None
    banner_text: NameStr | None = None


class OrganizationCreate(OrganizationBase):
    """Pydantic model for creating an organization resource."""
    pass


class OrganizationUpdate(DispatchBase):
    """Pydantic model for updating an organization resource."""
    id: PrimaryKey | None = None
    description: str | None = None
    default: bool | None = False
    banner_enabled: bool | None = False
    banner_color: str | None = None
    banner_text: NameStr | None = None


class OrganizationRead(OrganizationBase):
    """Pydantic model for reading an organization resource."""
    id: PrimaryKey | None = None
    slug: OrganizationSlug | None = None


class OrganizationPagination(Pagination):
    """Pydantic model for paginated organization results."""
    items: list[OrganizationRead] = []
