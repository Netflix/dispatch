from datetime import datetime
from pydantic import Field
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    PrimaryKeyConstraint,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    NameStr,
    Pagination,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
)
from dispatch.plugin.models import PluginEventRead, PluginEvent
from dispatch.project.models import ProjectRead

assoc_cost_model_activities = Table(
    "assoc_cost_model_activities",
    Base.metadata,
    Column("cost_model_id", Integer, ForeignKey("cost_model.id", ondelete="CASCADE")),
    Column(
        "cost_model_activity_id",
        Integer,
        ForeignKey("cost_model_activity.id", ondelete="CASCADE"),
    ),
    PrimaryKeyConstraint("cost_model_id", "cost_model_activity_id"),
)


# SQLAlchemy Model
class CostModelActivity(Base):
    id = Column(Integer, primary_key=True)
    plugin_event_id = Column(Integer, ForeignKey(PluginEvent.id, ondelete="CASCADE"))
    plugin_event = relationship(PluginEvent, backref="plugin_event")
    response_time_seconds = Column(Integer, default=300)
    enabled = Column(Boolean, default=True)


class CostModel(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    enabled = Column(Boolean)
    activities = relationship(
        "CostModelActivity",
        secondary=assoc_cost_model_activities,
        lazy="subquery",
        backref="cost_model",
    )
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic Models
class CostModelActivityBase(DispatchBase):
    """Base class for cost model activity resources"""
    plugin_event: PluginEventRead
    response_time_seconds: int | None = 300
    enabled: bool | None = Field(True, nullable=True)


class CostModelActivityCreate(CostModelActivityBase):
    id: PrimaryKey | None = None


class CostModelActivityRead(CostModelActivityBase):
    id: PrimaryKey


class CostModelActivityUpdate(CostModelActivityBase):
    id: PrimaryKey | None


class CostModelBase(DispatchBase):
    name: NameStr
    description: str | None = Field(None, nullable=True)
    enabled: bool | None = Field(True, nullable=True)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    project: ProjectRead


class CostModelUpdate(CostModelBase):
    id: PrimaryKey
    activities: list[CostModelActivityUpdate] | None = []


class CostModelCreate(CostModelBase):
    activities: list[CostModelActivityCreate] | None = []


class CostModelRead(CostModelBase):
    id: PrimaryKey
    activities: list[CostModelActivityRead] | None = []


class CostModelPagination(Pagination):
    items: list[CostModelRead] = []
