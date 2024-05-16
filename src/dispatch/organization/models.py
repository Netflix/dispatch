from slugify import slugify
from pydantic import Field
from pydantic.color import Color


from sqlalchemy.event import listen
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType


from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, OrganizationSlug, PrimaryKey, Pagination


class Organization(Base):
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
    """Creates a resonable slug based on organization name."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value, separator="_")


listen(Organization.name, "set", generate_slug)


class OrganizationBase(DispatchBase):
    id: PrimaryKey | None
    name: NameStr
    description: str | None = Field(None, nullable=True)
    default: bool | None = Field(False, nullable=True)
    banner_enabled: bool | None = Field(False, nullable=True)
    banner_color: Color | None = Field(None, nullable=True)
    banner_text: NameStr | None = Field(None, nullable=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(DispatchBase):
    id: PrimaryKey | None
    description: str | None = Field(None, nullable=True)
    default: bool | None = Field(False, nullable=True)
    banner_enabled: bool | None = Field(False, nullable=True)
    banner_color: Color | None = Field(None, nullable=True)
    banner_text: NameStr | None = Field(None, nullable=True)


class OrganizationRead(OrganizationBase):
    id: PrimaryKey | None
    slug: OrganizationSlug | None


class OrganizationPagination(Pagination):
    items: list[OrganizationRead] = []
