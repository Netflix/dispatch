from pydantic.networks import EmailStr
from slugify import slugify
from typing import List, Optional
from pydantic import Field

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, PrimaryKey

from dispatch.organization.models import Organization, OrganizationRead


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    default = Column(Boolean, default=False)
    color = Column(String)

    annual_employee_cost = Column(Integer, default=50000)
    business_year_hours = Column(Integer, default=2080)

    owner_email = Column(String)
    owner_conversation = Column(String)

    organization_id = Column(Integer, ForeignKey(Organization.id))
    organization = relationship("Organization")

    @hybrid_property
    def slug(self):
        return slugify(self.name)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class ProjectBase(DispatchBase):
    id: Optional[PrimaryKey]
    name: NameStr
    owner_email: Optional[EmailStr] = Field(None, nullable=True)
    owner_conversation: Optional[str] = Field(None, nullable=True)
    annual_employee_cost: Optional[int]
    business_year_hours: Optional[int]
    description: Optional[str] = Field(None, nullable=True)
    default: bool = False
    color: Optional[str] = Field(None, nullable=True)


class ProjectCreate(ProjectBase):
    organization: OrganizationRead


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: Optional[PrimaryKey]


class ProjectPagination(DispatchBase):
    total: int
    items: List[ProjectRead] = []
