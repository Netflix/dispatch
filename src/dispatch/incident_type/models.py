from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.enums import Visibility
from dispatch.models import Base, DispatchBase


class IncidentType(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    slug = Column(String)
    description = Column(String)
    visibility = Column(String, default=Visibility.open)

    template_document_id = Column(Integer, ForeignKey("document.id"))
    template_document = relationship("Document")

    commander_service_id = Column(Integer, ForeignKey("service.id"))
    commander_service = relationship("Service")

    search_vector = Column(TSVectorType("name", "description"))


class Document(DispatchBase):
    id: int
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str


class Service(DispatchBase):
    id: int
    name: Optional[str] = None
    external_id: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


# Pydantic models...
class IncidentTypeBase(DispatchBase):
    name: str
    description: Optional[str]


class IncidentTypeCreate(IncidentTypeBase):
    template_document: Optional[Document]
    commander_service: Optional[Service]


class IncidentTypeUpdate(IncidentTypeBase):
    id: int
    visibility: Optional[Visibility]
    template_document: Optional[Document]
    commander_service: Optional[Service]


class IncidentTypeRead(IncidentTypeBase):
    id: int
    visibility: Optional[Visibility]
    template_document: Optional[Document]
    commander_service: Optional[Service]


class IncidentTypeNested(IncidentTypeBase):
    id: int


class IncidentTypePagination(DispatchBase):
    total: int
    items: List[IncidentTypeRead] = []
