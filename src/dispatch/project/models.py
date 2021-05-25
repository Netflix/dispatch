from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase

from dispatch.organization.models import OrganizationCreate


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    default = Column(Boolean, default=False)
    color = Column(String)

    organization_id = Column(Integer, ForeignKey("dispatch.organization.id"))

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
