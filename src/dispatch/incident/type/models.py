from typing import List, Optional
from pydantic import validator, Field, AnyHttpUrl
from dispatch.models import NameStr, PrimaryKey

from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, JSON
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen

from sqlalchemy_utils import TSVectorType

from dispatch.cost_model.models import CostModelRead
from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, ProjectMixin, Pagination
from dispatch.plugin.models import PluginMetadata
from dispatch.project.models import ProjectRead
from dispatch.service.models import ServiceRead


class IncidentType(ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)
    exclude_from_metrics = Column(Boolean, default=False)

    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)
    visibility = Column(String, default=Visibility.open)
    plugin_metadata = Column(JSON, default=[])

    incident_template_document_id = Column(Integer, ForeignKey("document.id"))
    incident_template_document = relationship(
        "Document", foreign_keys=[incident_template_document_id]
    )

    executive_template_document_id = Column(Integer, ForeignKey("document.id"))
    executive_template_document = relationship(
        "Document", foreign_keys=[executive_template_document_id]
    )

    review_template_document_id = Column(Integer, ForeignKey("document.id"))
    review_template_document = relationship("Document", foreign_keys=[review_template_document_id])

    tracking_template_document_id = Column(Integer, ForeignKey("document.id"))
    tracking_template_document = relationship(
        "Document", foreign_keys=[tracking_template_document_id]
    )

    commander_service_id = Column(Integer, ForeignKey("service.id"))
    commander_service = relationship("Service", foreign_keys=[commander_service_id])

    liaison_service_id = Column(Integer, ForeignKey("service.id"))
    liaison_service = relationship("Service", foreign_keys=[liaison_service_id])

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))

    cost_model_id = Column(Integer, ForeignKey("cost_model.id"), nullable=True, default=None)
    cost_model = relationship(
        "CostModel",
        foreign_keys=[cost_model_id],
    )

    # Sets the channel description for the incidents of this type
    channel_description = Column(String, nullable=True)
    # Optionally add on-call name to the channel description
    description_service_id = Column(Integer, ForeignKey("service.id"))
    description_service = relationship("Service", foreign_keys=[description_service_id])

    @hybrid_method
    def get_meta(self, slug):
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m


listen(IncidentType.default, "set", ensure_unique_default_per_project)


class Document(DispatchBase):
    id: PrimaryKey
    name: NameStr
    resource_type: Optional[str] = Field(None, nullable=True)
    resource_id: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)
    weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)


# Pydantic models...
class IncidentTypeBase(DispatchBase):
    name: NameStr
    visibility: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    incident_template_document: Optional[Document]
    executive_template_document: Optional[Document]
    review_template_document: Optional[Document]
    tracking_template_document: Optional[Document]
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False
    project: Optional[ProjectRead]
    plugin_metadata: List[PluginMetadata] = []
    cost_model: Optional[CostModelRead] = None
    channel_description: Optional[str] = Field(None, nullable=True)
    description_service: Optional[ServiceRead]

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class IncidentTypeCreate(IncidentTypeBase):
    pass


class IncidentTypeUpdate(IncidentTypeBase):
    id: PrimaryKey = None


class IncidentTypeRead(IncidentTypeBase):
    id: PrimaryKey


class IncidentTypeReadMinimal(DispatchBase):
    id: PrimaryKey
    name: NameStr
    visibility: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False


class IncidentTypePagination(Pagination):
    items: List[IncidentTypeRead] = []
