from slugify import slugify
from pydantic import Field, constr

from typing import List, Optional

from sqlalchemy.event import listen
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType


from dispatch.database.core import Base
from dispatch.models import DispatchBase, PrimaryKey


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

OrganizationName = constr(regex=r"^(?!\s*$).+")


class OrganizationBase(DispatchBase):
    id: Optional[PrimaryKey]
    name: OrganizationName
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[str] = Field(None, nullable=True)
    banner_text: Optional[str] = Field(None, nullable=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: Optional[PrimaryKey]
    slug: Optional[str]


class OrganizationPagination(DispatchBase):
    total: int
    items: List[OrganizationRead] = []
