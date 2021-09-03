from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, JSON, Boolean

from dispatch.database.core import Base
from dispatch.plugin.models import PluginInstance, PluginInstanceRead


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
    creator_id = Column(Integer, ForeignKey("participant.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))

    creator = relationship(
        "Participant", backref="created_monitor_instances", foreign_keys=[creator_id]
    )
    enabled = Column(Boolean, default=True)
    status = Column(JSON)


class MonitorBase(ResourceBase):
    id: PrimaryKey
    resource_id: str
    plugin_instance: PluginInstanceRead


class MonitorCreate(MonitorBase):
    pass


class MonitorUpdate(MonitorBase):
    pass


class MonitorRead(MonitorBase):
    pass
