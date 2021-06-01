from typing import List, Optional
from pydantic import validator

from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, JSON
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen

from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, ProjectMixin
from dispatch.plugin.models import PluginMetadata
from dispatch.project.models import ProjectRead


class IncidentType(ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)
    exclude_from_metrics = Column(Boolean, default=False)

    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)
    visibility = Column(String, default=Visibility.open.value)
    plugin_metadata = Column(JSON, default=[])

    template_document_id = Column(Integer, ForeignKey("document.id"))
    template_document = relationship("Document")

    commander_service_id = Column(Integer, ForeignKey("service.id"))
    commander_service = relationship("Service", foreign_keys=[commander_service_id])

    liaison_service_id = Column(Integer, ForeignKey("service.id"))
    liaison_service = relationship("Service", foreign_keys=[liaison_service_id])

    search_vector = Column(TSVectorType("name", "description"))

    @hybrid_method
    def get_meta(self, slug):
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m


listen(IncidentType.default, "set", ensure_unique_default_per_project)


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
    visibility: Optional[str]
    description: Optional[str]
    enabled: Optional[bool]
    template_document: Optional[Document]
    commander_service: Optional[Service]
    liaison_service: Optional[Service]
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False
    project: Optional[ProjectRead]
    plugin_metadata: List[PluginMetadata] = []

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class IncidentTypeCreate(IncidentTypeBase):
    pass


class IncidentTypeUpdate(IncidentTypeBase):
    id: int


class IncidentTypeRead(IncidentTypeBase):
    id: int


class IncidentTypePagination(DispatchBase):
    total: int
    items: List[IncidentTypeRead] = []
