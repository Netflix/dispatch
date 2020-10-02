from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import validator
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Table
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.document.models import DocumentCreate
from dispatch.models import DispatchBase, ResourceMixin, TimeStampMixin
from dispatch.participant.models import ParticipantRead
from dispatch.plugin.models import PluginRead


class WorkflowInstanceStatus(str, Enum):
    submitted = "submitted"
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"


# Association tables for many to many relationships
assoc_workflow_instances_artifacts = Table(
    "workflow_instance_artifact",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id")),
    Column("workflow_instance_id", Integer, ForeignKey("workflow_instance.id")),
    PrimaryKeyConstraint("document_id", "workflow_instance_id"),
)

assoc_workflow_incident_priorities = Table(
    "workflow_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("workflow_id", Integer, ForeignKey("workflow.id")),
    PrimaryKeyConstraint("incident_priority_id", "workflow_id"),
)

assoc_workflow_incident_types = Table(
    "workflow_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("workflow_id", Integer, ForeignKey("workflow.id")),
    PrimaryKeyConstraint("incident_type_id", "workflow_id"),
)

assoc_workflow_terms = Table(
    "workflow_term",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("workflow_id", Integer, ForeignKey("workflow.id")),
    PrimaryKeyConstraint("term_id", "workflow_id"),
)


class Workflow(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean, default=True)
    parameters = Column(JSON, default=[])
    resource_id = Column(String)
    plugin_id = Column(Integer, ForeignKey("plugin.id"))
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


class WorkflowInstance(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow.id"))
    incident_id = Column(Integer, ForeignKey("incident.id"))
    parameters = Column(JSON, default=[])
    run_reason = Column(String)
    creator_id = Column(Integer, ForeignKey("participant.id"))
    creator = relationship(
        "Participant", backref="created_workflow_instances", foreign_keys=[creator_id]
    )
    status = Column(String, default=WorkflowInstanceStatus.submitted)
    artifacts = relationship(
        "Document", secondary=assoc_workflow_instances_artifacts, backref="workflow_instance"
    )


# Pydantic models...
class WorkflowBase(DispatchBase):
    name: str
    resource_id: str
    plugin: Optional[PluginRead]
    parameters: Optional[List[dict]] = []
    enabled: Optional[bool]
    description: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    id: int


class WorkflowRead(WorkflowBase):
    id: int

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return "No Description"
        return v


class WorkflowNested(WorkflowRead):
    pass


class WorkflowPagination(DispatchBase):
    total: int
    items: List[WorkflowRead] = []


class WorkflowInstanceBase(DispatchBase):
    resource_type: Optional[str]
    resource_id: Optional[str]
    weblink: Optional[str]
    status: Optional[WorkflowInstanceStatus]
    parameters: Optional[List[dict]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    run_reason: Optional[str]
    artifacts: Optional[List[DocumentCreate]] = []


class WorkflowInstanceCreate(WorkflowInstanceBase):
    workflow: dict  # TODO define a required ID
    incident: dict  # TODO define a required ID
    creator: dict  # TODO define a required email


class WorkflowInstanceUpdate(WorkflowInstanceBase):
    pass


class WorkflowInstanceRead(WorkflowInstanceBase):
    id: int
    workflow: WorkflowRead
    creator: ParticipantRead


class WorkflowInstancePagination(DispatchBase):
    total: int
    items: List[WorkflowInstanceRead] = []
