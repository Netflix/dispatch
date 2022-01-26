from slugify import slugify
from pydantic import Field
from pydantic.color import Color

from typing import List, Optional

from sqlalchemy.event import listen
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType


from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, OrganizationSlug, PrimaryKey


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
    id: Optional[PrimaryKey]
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[NameStr] = Field(None, nullable=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(DispatchBase):
    id: Optional[PrimaryKey]
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[NameStr] = Field(None, nullable=True)


class OrganizationRead(OrganizationBase):
    id: Optional[PrimaryKey]
    slug: Optional[OrganizationSlug]


class OrganizationPagination(DispatchBase):
    total: int
    items: List[OrganizationRead] = []
