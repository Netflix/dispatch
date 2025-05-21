"""Models for workflow functionality in the Dispatch application."""

from datetime import datetime

from pydantic import field_validator
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Table
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.document.models import DocumentCreate
from dispatch.models import (
    DispatchBase,
    NameStr,
    Pagination,
    PrimaryKey,
    ProjectMixin,
    ResourceBase,
    ResourceMixin,
    TimeStampMixin,
)
from dispatch.participant.models import ParticipantRead
from dispatch.plugin.models import PluginInstance, PluginInstanceReadMinimal
from dispatch.project.models import ProjectRead

from .enums import WorkflowInstanceStatus


# Association tables for many to many relationships
assoc_workflow_instances_artifacts = Table(
    "workflow_instance_artifact",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("workflow_instance_id", Integer, ForeignKey("workflow_instance.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "workflow_instance_id"),
)

assoc_workflow_incident_priorities = Table(
    "workflow_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id", ondelete="CASCADE")),
    Column("workflow_id", Integer, ForeignKey("workflow.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_priority_id", "workflow_id"),
)

assoc_workflow_incident_types = Table(
    "workflow_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id", ondelete="CASCADE")),
    Column("workflow_id", Integer, ForeignKey("workflow.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_type_id", "workflow_id"),
)

assoc_workflow_terms = Table(
    "workflow_term",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id", ondelete="CASCADE")),
    Column("workflow_id", Integer, ForeignKey("workflow.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("term_id", "workflow_id"),
)


class Workflow(Base, ProjectMixin, TimeStampMixin):
    """SQLAlchemy model for workflow resources."""
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean, default=True)
    parameters = Column(JSON, default=[])
    resource_id = Column(String)
    plugin_instance_id = Column(Integer, ForeignKey(PluginInstance.id))
    plugin_instance = relationship(PluginInstance)
    instances = relationship("WorkflowInstance")
    incident_priorities = relationship(
        "IncidentPriority", assoc_workflow_incident_priorities
    )
    incident_types = relationship(
        "IncidentType", assoc_workflow_incident_types
    )
    terms = relationship(
        "Term", assoc_workflow_terms
    )
    search_vector = Column(TSVectorType("name", "description"))


class WorkflowInstance(Base, ResourceMixin):
    """SQLAlchemy model for workflow instance resources."""
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow.id"))
    parameters = Column(JSON, default=[])
    run_reason = Column(String)
    creator_id = Column(Integer, ForeignKey("participant.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    signal_id = Column(Integer, ForeignKey("signal.id", ondelete="CASCADE"))
    creator = relationship("Participant")
    status = Column(String, default=WorkflowInstanceStatus.submitted)
    artifacts = relationship(
        "Document", assoc_workflow_instances_artifacts
    )


class WorkflowIncident(DispatchBase):
    """Pydantic model for workflow incident reference."""
    id: PrimaryKey
    name: NameStr | None


class WorkflowCase(DispatchBase):
    """Pydantic model for workflow case reference."""
    id: PrimaryKey
    name: NameStr | None


class WorkflowSignal(DispatchBase):
    """Pydantic model for workflow signal reference."""
    id: PrimaryKey
    name: NameStr | None


# Pydantic models...
class WorkflowBase(DispatchBase):
    """Base Pydantic model for workflow resources."""
    name: NameStr
    resource_id: str
    plugin_instance: PluginInstanceReadMinimal
    parameters: list[dict[str, object]] | None = None
    enabled: bool | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkflowCreate(WorkflowBase):
    """Pydantic model for creating a workflow resource."""
    project: ProjectRead


class WorkflowUpdate(WorkflowBase):
    """Pydantic model for updating a workflow resource."""
    id: PrimaryKey


class WorkflowRead(WorkflowBase):
    """Pydantic model for reading a workflow resource."""
    id: PrimaryKey

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, v: str | None):
        """Sets the description."""
        if not v:
            return "No Description"
        return v


class WorkflowPagination(Pagination):
    """Pydantic model for paginated workflow results."""
    items: list[WorkflowRead] = []


class WorkflowInstanceBase(ResourceBase):
    """Base Pydantic model for workflow instance resources."""
    artifacts: list[DocumentCreate] | None = None
    created_at: datetime | None = None
    parameters: list[dict[str, object]] | None = None
    run_reason: str | None = None
    status: WorkflowInstanceStatus | None = None
    updated_at: datetime | None = None
    incident: WorkflowIncident | None = None
    case: WorkflowCase | None = None
    signal: WorkflowSignal | None = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    """Pydantic model for creating a workflow instance resource."""
    creator: ParticipantRead | None = None
    incident: WorkflowIncident | None = None
    case: WorkflowCase | None = None
    signal: WorkflowSignal | None = None


class WorkflowInstanceUpdate(WorkflowInstanceBase):
    """Pydantic model for updating a workflow instance resource."""


class WorkflowInstanceRead(WorkflowInstanceBase):
    """Pydantic model for reading a workflow instance resource."""
    id: PrimaryKey
    workflow: WorkflowRead | None = None
    creator: ParticipantRead | None = None


class WorkflowInstancePagination(Pagination):
    """Pydantic model for paginated workflow instance results."""
    items: list[WorkflowInstanceRead] = []
