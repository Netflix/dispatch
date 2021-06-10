from slugify import slugify
from typing import List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase

from dispatch.organization.models import Organization, OrganizationCreate


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)
    default = Column(Boolean, default=False)
    color = Column(String)

    organization_id = Column(Integer, ForeignKey(Organization.id))

    @hybrid_property
    def slug(self, name):
        return slugify(name)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class ProjectBase(DispatchBase):
    id: Optional[int]
    name: str
    description: Optional[str]
    default: bool = False
    color: Optional[str]


class ProjectCreate(ProjectBase):
    organization: OrganizationCreate


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: Optional[int]


class ProjectPagination(DispatchBase):
    total: int
    items: List[ProjectRead] = []
