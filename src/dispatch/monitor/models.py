from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, JSON, Boolean

from dispatch.database.core import Base
from dispatch.incident.models import IncidentRead
from dispatch.plugin.models import PluginInstance, PluginInstanceRead
from dispatch.participant.models import ParticipantRead
from dispatch.models import (
    PrimaryKey,
    ResourceBase,
    ResourceMixin,
    TimeStampMixin,
)


class Monitor(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    plugin_instance_id = Column(Integer, ForeignKey(PluginInstance.id))
    plugin_instance = relationship(PluginInstance, backref="monitors")
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    incident = relationship("Incident", backref="monitors", foreign_keys=[incident_id])
    creator_id = Column(Integer, ForeignKey("participant.id"))
    creator = relationship(
        "Participant", backref="created_monitor_instances", foreign_keys=[creator_id]
    )
    enabled = Column(Boolean, default=True)
    status = Column(JSON)


class MonitorBase(ResourceBase):
    enabled: Optional[bool]
    status: Optional[dict]


class MonitorCreate(MonitorBase):
    plugin_instance: PluginInstanceRead
    creator: ParticipantRead
    incident: IncidentRead


class MonitorUpdate(MonitorBase):
    id: PrimaryKey


class MonitorRead(MonitorBase):
    id: PrimaryKey
