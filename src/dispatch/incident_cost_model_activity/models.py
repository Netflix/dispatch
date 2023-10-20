from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional

from dispatch.database.core import Base
from dispatch.models import DispatchBase, PrimaryKey, Field
from dispatch.plugin.models import PluginEventRead, PluginEvent


# SQLAlchemy Model
class IncidentCostModelActivity(Base):
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(PluginEvent.id, ondelete="CASCADE"))
    event = relationship(PluginEvent, backref="plugin_event")
    response_time_seconds = Column(Integer, default=300)
    enabled = Column(Boolean, default=True)


# Pydantic Models
class IncidentCostModelActivityBase(DispatchBase):
    event: PluginEventRead
    response_time_seconds: Optional[int] = 300
    enabled: Optional[bool] = Field(True, nullable=True)


class IncidentCostModelActivityCreate(IncidentCostModelActivityBase):
    pass


class IncidentCostModelActivityRead(IncidentCostModelActivityBase):
    id: PrimaryKey


class IncidentCostModelActivityUpdate(IncidentCostModelActivityBase):
    id: Optional[PrimaryKey]
