from datetime import datetime
from pydantic import Field
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from typing import List, Optional

from dispatch.database.core import Base
from dispatch.incident_cost_model_activity.models import (
    IncidentCostModelActivity,
    IncidentCostModelActivityCreate,
    IncidentCostModelActivityRead,
    IncidentCostModelActivityUpdate,
)
from dispatch.models import (
    DispatchBase,
    NameStr,
    Pagination,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
)
from dispatch.project.models import ProjectRead

assoc_incident_cost_model_activities = Table(
    "assoc_incident_cost_model_activities",
    Base.metadata,
    Column(
        "incident_cost_model_id", Integer, ForeignKey("incident_cost_model.id", ondelete="CASCADE")
    ),
    Column(
        "incident_cost_model_activity_id",
        Integer,
        ForeignKey("incident_cost_model_activity.id", ondelete="CASCADE"),
    ),
    PrimaryKeyConstraint("incident_cost_model_id", "incident_cost_model_activity_id"),
)


# SQLAlchemy Model
class IncidentCostModel(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    activities = relationship(
        "IncidentCostModelActivity",
        secondary=assoc_incident_cost_model_activities,
        lazy="subquery",
        backref="incident_cost_model",
    )


# Pydantic Models
class IncidentCostModelBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool] = Field(True, nullable=True)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    project: ProjectRead


class IncidentCostModelUpdate(IncidentCostModelBase):
    id: PrimaryKey
    activities: Optional[List[IncidentCostModelActivityUpdate]] = []


class IncidentCostModelCreate(IncidentCostModelBase):
    activities: Optional[List[IncidentCostModelActivityCreate]] = []


class IncidentCostModelRead(IncidentCostModelBase):
    id: PrimaryKey
    activities: Optional[List[IncidentCostModelActivityRead]] = []


class IncidentCostModelPagination(Pagination):
    items: List[IncidentCostModelRead] = []
