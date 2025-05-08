"""Models for case types and related entities in the Dispatch application."""
from pydantic import field_validator, AnyHttpUrl

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.cost_model.models import CostModelRead
from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, NameStr, Pagination, PrimaryKey, ProjectMixin
from dispatch.plugin.models import PluginMetadata
from dispatch.project.models import ProjectRead


class CaseType(ProjectMixin, Base):
    """SQLAlchemy model for case types, representing different types of cases in the system."""
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
    auto_close = Column(Boolean, default=False, server_default=false())

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))

    # relationships
    case_template_document_id = Column(Integer, ForeignKey("document.id"))
    case_template_document = relationship("Document")

    oncall_service_id = Column(Integer, ForeignKey("service.id"))
    oncall_service = relationship("Service")

    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))
    incident_type = relationship("IncidentType")

    cost_model_id = Column(Integer, ForeignKey("cost_model.id"), nullable=True, default=None)
    cost_model = relationship(
        "CostModel",
    )

    @hybrid_method
    def get_meta(self, slug):
        """Retrieve plugin metadata by slug."""
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m


listen(CaseType.default, "set", ensure_unique_default_per_project)


# Pydantic models
class Document(DispatchBase):
    """Pydantic model for a document related to a case type."""
    id: PrimaryKey
    description: str | None = None
    name: NameStr
    resource_id: str | None = None
    resource_type: str | None = None
    weblink: AnyHttpUrl | None = None


class IncidentType(DispatchBase):
    """Pydantic model for an incident type related to a case type."""
    id: PrimaryKey
    description: str | None = None
    name: NameStr
    visibility: str | None = None


class Service(DispatchBase):
    """Pydantic model for a service related to a case type."""
    id: PrimaryKey
    description: str | None = None
    external_id: str
    is_active: bool | None = None
    name: NameStr
    type: str | None = None


class CaseTypeBase(DispatchBase):
    """Base Pydantic model for case types, used for shared fields."""
    case_template_document: Document | None = None
    conversation_target: str | None = None
    default: bool | None = False
    description: str | None = None
    enabled: bool | None = True
    exclude_from_metrics: bool | None = False
    incident_type: IncidentType | None = None
    name: NameStr
    oncall_service: Service | None = None
    plugin_metadata: list[PluginMetadata] = []
    project: ProjectRead | None = None
    visibility: str | None = None
    cost_model: CostModelRead | None = None
    auto_close: bool | None = False

    @field_validator("plugin_metadata", mode="before")
    @classmethod
    def replace_none_with_empty_list(cls, value):
        """Ensure plugin_metadata is always a list, replacing None with an empty list."""
        return [] if value is None else value


class CaseTypeCreate(CaseTypeBase):
    """Pydantic model for creating a new case type."""
    pass


class CaseTypeUpdate(CaseTypeBase):
    """Pydantic model for updating an existing case type."""
    id: PrimaryKey | None = None


class CaseTypeRead(CaseTypeBase):
    """Pydantic model for reading a case type from the database."""
    id: PrimaryKey


class CaseTypePagination(Pagination):
    """Pydantic model for paginated case type results."""
    items: list[CaseTypeRead] = []
