"""Models for incident type resources in the Dispatch application."""

from pydantic import field_validator, AnyHttpUrl

from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, JSON
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType


from dispatch.cost_model.models import CostModelRead
from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, ProjectMixin, Pagination
from dispatch.models import NameStr, PrimaryKey
from dispatch.plugin.models import PluginMetadata
from dispatch.project.models import ProjectRead
from dispatch.service.models import ServiceRead


class IncidentType(ProjectMixin, Base):
    """SQLAlchemy model for incident type resources."""

    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)
    exclude_from_metrics = Column(Boolean, default=False)

    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)
    visibility = Column(String, default=Visibility.open)
    exclude_from_reminders = Column(Boolean, default=False)
    exclude_from_review = Column(Boolean, default=False)
    plugin_metadata = Column(JSON, default=[])
    task_plugin_metadata = Column(JSON, default=[])

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

    channel_description = Column(String, nullable=True)
    description_service_id = Column(Integer, ForeignKey("service.id"))
    description_service = relationship("Service", foreign_keys=[description_service_id])

    @hybrid_method
    def get_meta(self, slug):
        """Retrieve plugin metadata by slug."""
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m

    @hybrid_method
    def get_task_meta(self, slug):
        """Retrieve task plugin metadata by slug."""
        if not self.task_plugin_metadata:
            return

        for m in self.task_plugin_metadata:
            if m["slug"] == slug:
                return m


listen(IncidentType.default, "set", ensure_unique_default_per_project)


class Document(DispatchBase):
    """Pydantic model for a document related to an incident type."""

    id: PrimaryKey
    name: NameStr
    resource_type: str | None = None
    resource_id: str | None = None
    description: str | None = None
    weblink: AnyHttpUrl | None = None


# Pydantic models...
class IncidentTypeBase(DispatchBase):
    """Base Pydantic model for incident type resources."""

    name: NameStr
    visibility: str | None = None
    description: str | None = None
    enabled: bool | None = None
    incident_template_document: Document | None = None
    executive_template_document: Document | None = None
    review_template_document: Document | None = None
    tracking_template_document: Document | None = None
    exclude_from_metrics: bool | None = False
    exclude_from_reminders: bool | None = False
    exclude_from_review: bool | None = False
    default: bool | None = False
    project: ProjectRead | None = None
    plugin_metadata: list[PluginMetadata] = []
    cost_model: CostModelRead | None = None
    channel_description: str | None = None
    description_service: ServiceRead | None = None
    task_plugin_metadata: list[PluginMetadata] = []

    @field_validator("plugin_metadata", mode="before")
    @classmethod
    def replace_none_with_empty_list(cls, value):
        """Ensure plugin_metadata is always a list, replacing None with an empty list."""
        return [] if value is None else value


class IncidentTypeCreate(IncidentTypeBase):
    """Pydantic model for creating an incident type resource."""

    pass


class IncidentTypeUpdate(IncidentTypeBase):
    """Pydantic model for updating an incident type resource."""

    id: PrimaryKey | None = None


class IncidentTypeRead(IncidentTypeBase):
    """Pydantic model for reading an incident type resource."""

    id: PrimaryKey


class IncidentTypeReadMinimal(DispatchBase):
    """Pydantic model for reading a minimal incident type resource."""

    id: PrimaryKey
    name: NameStr
    visibility: str | None = None
    description: str | None = None
    enabled: bool | None = None
    exclude_from_metrics: bool | None = False
    default: bool | None = False


class IncidentTypePagination(Pagination):
    """Pydantic model for paginated incident type results."""

    items: list[IncidentTypeRead] = []
