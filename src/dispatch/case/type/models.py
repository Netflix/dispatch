from typing import List, Optional

from pydantic import Field, validator, AnyHttpUrl
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.cost_model.models import CostModelRead
from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, NameStr, Pagination, PrimaryKey, ProjectMixin
from dispatch.plugin.models import PluginMetadata
from dispatch.project.models import ProjectRead


class CaseType(ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    visibility = Column(String, default=Visibility.open)
    default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    exclude_from_metrics = Column(Boolean, default=False)
    plugin_metadata = Column(JSON, default=[])
    conversation_target = Column(String)

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))

    # relationships
    case_template_document_id = Column(Integer, ForeignKey("document.id"))
    case_template_document = relationship("Document", foreign_keys=[case_template_document_id])

    oncall_service_id = Column(Integer, ForeignKey("service.id"))
    oncall_service = relationship("Service", foreign_keys=[oncall_service_id])

    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))
    incident_type = relationship("IncidentType", foreign_keys=[incident_type_id])

    cost_model_id = Column(Integer, ForeignKey("cost_model.id"), nullable=True, default=None)
    cost_model = relationship(
        "CostModel",
        foreign_keys=[cost_model_id],
    )

    @hybrid_method
    def get_meta(self, slug):
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m


listen(CaseType.default, "set", ensure_unique_default_per_project)


# Pydantic models
class Document(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr
    resource_id: Optional[str] = Field(None, nullable=True)
    resource_type: Optional[str] = Field(None, nullable=True)
    weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)


class IncidentType(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr
    visibility: Optional[str] = Field(None, nullable=True)


class Service(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    external_id: str
    is_active: Optional[bool] = None
    name: NameStr
    type: Optional[str] = Field(None, nullable=True)


class CaseTypeBase(DispatchBase):
    case_template_document: Optional[Document]
    conversation_target: Optional[str]
    default: Optional[bool] = False
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    exclude_from_metrics: Optional[bool] = False
    incident_type: Optional[IncidentType]
    name: NameStr
    oncall_service: Optional[Service]
    plugin_metadata: List[PluginMetadata] = []
    project: Optional[ProjectRead]
    visibility: Optional[str] = Field(None, nullable=True)
    cost_model: Optional[CostModelRead] = None

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class CaseTypeCreate(CaseTypeBase):
    pass


class CaseTypeUpdate(CaseTypeBase):
    id: PrimaryKey = None


class CaseTypeRead(CaseTypeBase):
    id: PrimaryKey


class CaseTypePagination(Pagination):
    items: List[CaseTypeRead] = []
