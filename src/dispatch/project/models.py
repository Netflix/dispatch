from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import ContactBase, DispatchBase


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    search_vector = Column(TSVectorType("name", "description", weights={"name": "A", "notes": "B"}))


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
