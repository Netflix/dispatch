from typing import List, Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import ContactBase, DispatchBase


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )

    __table_args__ = {"schema": "public"}


class ProjectBase(ContactBase):
    name: str
    description: Optional[str]


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int


class ProjectPagination(DispatchBase):
    total: int
    items: List[ProjectRead] = []
