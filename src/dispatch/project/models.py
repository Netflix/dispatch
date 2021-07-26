from slugify import slugify
from typing import List, Optional
from pydantic import Field, constr

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, PrimaryKey

from dispatch.organization.models import Organization, OrganizationCreate


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    default = Column(Boolean, default=False)
    color = Column(String)

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
    name: constr(min_length=3)
    description: Optional[str] = Field(None, nullable=True)
    default: bool = False
    color: Optional[str] = Field(None, nullable=True)


class ProjectCreate(ProjectBase):
    organization: OrganizationCreate


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: Optional[PrimaryKey]


class ProjectPagination(DispatchBase):
    total: int
    items: List[ProjectRead] = []
