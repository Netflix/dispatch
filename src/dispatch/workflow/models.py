from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import validator
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Table
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, ResourceMixin, TimeStampMixin


class WorkflowInstanceStatus(str, Enum):
    created = "Created"
    running = "Running"
    completed = "Completed"
    failed = "Failed"


assoc_workflow_instances_artifacts = Table(
    "workflow_instance_artifacts",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id")),
    Column("workflow_instance_id", Integer, ForeignKey("workflow_instance.id")),
    PrimaryKeyConstraint("document_id", "workflow_instance_id"),
)


class Workflow(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    parameters = Column(JSON)
    resource_id = Column(String)
    plugin_slug = Column(String, default="default-workflow")
    search_vector = Column(TSVectorType("name", "description"))
    instances = relationship("WorkflowInstance")


class WorkflowInstance(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflow.id"))
    creator_id = Column(Integer, ForeignKey("participant.id"))
    creator = relationship(
        "Participant", backref="created_workflow_instances", foreign_keys=[creator_id]
    )
    status = Column(String, default=WorkflowInstanceStatus.created)
    artifacts = relationship(
        "Document", secondary=assoc_workflow_instances_artifacts, backref="workflow_instance"
    )


# Pydantic models...
class WorkflowInstanceBase(DispatchBase):
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    pass


class WorkflowInstanceUpdate(WorkflowInstanceBase):
    pass


class WorkflowInstanceRead(WorkflowInstanceBase):
    pass


class WorkflowInstancePagination(DispatchBase):
    total: int
    items: List[WorkflowInstanceRead] = []


class WorkflowBase(DispatchBase):
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


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
