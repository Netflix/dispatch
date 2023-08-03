from datetime import datetime
from typing import List, Optional

from pydantic import validator, Field
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Table
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.document.models import DocumentCreate
from dispatch.models import (
    DispatchBase,
    NameStr,
    ResourceBase,
    ResourceMixin,
    TimeStampMixin,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)
from dispatch.participant.models import ParticipantRead
from dispatch.plugin.models import PluginInstance, PluginInstanceRead
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
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean, default=True)
    parameters = Column(JSON, default=[])
    resource_id = Column(String)
    plugin_instance_id = Column(Integer, ForeignKey(PluginInstance.id))
    plugin_instance = relationship(PluginInstance, backref="workflows")
    instances = relationship("WorkflowInstance", backref="workflow")
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_workflow_incident_priorities, backref="workflows"
    )
    incident_types = relationship(
        "IncidentType", secondary=assoc_workflow_incident_types, backref="workflows"
    )
    terms = relationship(
        "Term", secondary=assoc_workflow_terms, backref=backref("workflows", cascade="all")
    )

    search_vector = Column(TSVectorType("name", "description"))


class WorkflowInstance(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow.id"))
    parameters = Column(JSON, default=[])
    run_reason = Column(String)
    creator_id = Column(Integer, ForeignKey("participant.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    signal_id = Column(Integer, ForeignKey("signal.id", ondelete="CASCADE"))
    creator = relationship(
        "Participant", backref="created_workflow_instances", foreign_keys=[creator_id]
    )
    status = Column(String, default=WorkflowInstanceStatus.submitted)
    artifacts = relationship(
        "Document", secondary=assoc_workflow_instances_artifacts, backref="workflow_instance"
    )


class WorkflowIncident(DispatchBase):
    id: PrimaryKey
    name: Optional[NameStr]


class WorkflowCase(DispatchBase):
    id: PrimaryKey
    name: Optional[NameStr]


class WorkflowSignal(DispatchBase):
    id: PrimaryKey
    name: Optional[NameStr]


# Pydantic models...
class WorkflowBase(DispatchBase):
    name: NameStr
    resource_id: str
    plugin_instance: PluginInstanceRead
    parameters: Optional[List[dict]] = []
    enabled: Optional[bool]
    description: Optional[str] = Field(None, nullable=True)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    project: ProjectRead


class WorkflowUpdate(WorkflowBase):
    id: PrimaryKey = None


class WorkflowRead(WorkflowBase):
    id: PrimaryKey

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return "No Description"
        return v


class WorkflowPagination(Pagination):
    items: List[WorkflowRead] = []


class WorkflowInstanceBase(ResourceBase):
    artifacts: Optional[List[DocumentCreate]] = []
    created_at: Optional[datetime] = None
    parameters: Optional[List[dict]] = []
    run_reason: Optional[str] = Field(None, nullable=True)
    status: Optional[WorkflowInstanceStatus]
    updated_at: Optional[datetime] = None
    incident: Optional[WorkflowIncident]
    case: Optional[WorkflowCase]
    signal: Optional[WorkflowSignal]


class WorkflowInstanceCreate(WorkflowInstanceBase):
    creator: Optional[ParticipantRead]
    incident: Optional[WorkflowIncident]
    case: Optional[WorkflowCase]
    signal: Optional[WorkflowSignal]


class WorkflowInstanceUpdate(WorkflowInstanceBase):
    pass


class WorkflowInstanceRead(WorkflowInstanceBase):
    id: PrimaryKey
    workflow: WorkflowRead
    creator: Optional[ParticipantRead]


class WorkflowInstancePagination(Pagination):
    items: List[WorkflowInstanceRead] = []
