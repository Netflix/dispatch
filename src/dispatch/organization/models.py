from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class Organization(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    projects = relationship("Project")

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )

    __table_args__ = {"schema": "public"}


class OrganizationBase(Base):
    name: str
    description: Optional[str]


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: int


class OrganizationPagination(DispatchBase):
    total: int
    items: List[OrganizationRead] = []
