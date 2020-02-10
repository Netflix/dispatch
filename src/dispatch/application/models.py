from typing import Optional, List

from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, applications_incidents, TimeStampMixin


class Application(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    incidents = relationship("Incident", secondary=applications_incidents, backref="applications")
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class ApplicationBase(DispatchBase):
    name: str
    source: str
    uri: Optional[str]
    description: Optional[str]


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    id: int


class ApplicationRead(ApplicationBase):
    id: int


class ApplicationPagination(DispatchBase):
    items: List[ApplicationRead]
    total: int
