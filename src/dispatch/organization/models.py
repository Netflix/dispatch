from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class OrganizationContact(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    search_vector = Column(TSVectorType("name", "description", weights={"name": "A", "notes": "B"}))


class OrganizationBase(Base):
    name: str
    notes: Optional[str]


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: int


class OrganizationPagination(DispatchBase):
    total: int
    items: List[OrganizationRead] = []
