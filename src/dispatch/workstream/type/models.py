from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin
from dispatch.models import NameStr, PrimaryKey
from dispatch.project.models import ProjectRead


class WorkstreamType(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean, default=True)

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))

    # relationships
    document_template_id = Column(Integer, ForeignKey("document.id"))
    document_template = relationship("Document", foreign_keys=[document_template_id])

    oncall_service_id = Column(Integer, ForeignKey("service.id"))
    oncall_service = relationship("Service", foreign_keys=[oncall_service_id])


# Pydantic models


class Document(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr
    resource_id: Optional[str] = Field(None, nullable=True)
    resource_type: Optional[str] = Field(None, nullable=True)
    weblink: str


class Service(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    external_id: str
    is_active: Optional[bool] = None
    name: NameStr
    type: Optional[str] = Field(None, nullable=True)


class WorkstreamTypeBase(DispatchBase):
    description: Optional[str] = Field(None, nullable=True)
    document_template: Optional[Document]
    enabled: Optional[bool]
    name: NameStr
    oncall_service: Optional[Service]
    project: Optional[ProjectRead]


class WorkstreamTypeCreate(WorkstreamTypeBase):
    pass


class WorkstreamTypeUpdate(WorkstreamTypeBase):
    id: PrimaryKey = None


class WorkstreamTypeRead(WorkstreamTypeBase):
    id: PrimaryKey


class WorkstreamTypePagination(DispatchBase):
    total: int
    items: List[WorkstreamTypeRead] = []
