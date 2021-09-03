from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Table, Boolean

from dispatch.database.core import Base
from dispatch.plugin.models import PluginInstance, PluginInstanceRead


from dispatch.models import (
    DispatchBase,
    NameStr,
    ResourceBase,
    ResourceMixin,
    TimeStampMixin,
    ProjectMixin,
    PrimaryKey,
)


class Monitor(Base, ProjectMixin, TimeStampMixin):
    plugin_instance_id = Column(Integer, ForeignKey(PluginInstance.id))
    plugin_instance = relationship(PluginInstance, backref="monitors")
    instances = relationship("MonitorInstance", backref="monitor")


class MonitorInstance(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("participant.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))

    creator = relationship(
        "Participant", backref="created_workflow_instances", foreign_keys=[creator_id]
    )
    enabled = Column(Boolean, default=True)
    status = Column(JSON)
