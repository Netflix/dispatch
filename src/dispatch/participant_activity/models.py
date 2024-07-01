from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from dispatch.case.models import CaseRead
from dispatch.database.core import Base
from dispatch.incident.models import IncidentRead
from dispatch.models import DispatchBase, PrimaryKey
from dispatch.participant.models import ParticipantRead
from dispatch.plugin.models import PluginEvent, PluginEventRead


# SQLAlchemy Models
class ParticipantActivity(Base):
    id = Column(Integer, primary_key=True)

    plugin_event_id = Column(Integer, ForeignKey(PluginEvent.id))
    plugin_event = relationship(PluginEvent, foreign_keys=[plugin_event_id])

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, default=datetime.utcnow)

    participant_id = Column(Integer, ForeignKey("participant.id"))
    participant = relationship("Participant", foreign_keys=[participant_id])

    incident_id = Column(Integer, ForeignKey("incident.id"))
    incident = relationship("Incident", foreign_keys=[incident_id])

    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", foreign_keys=[case_id])


# Pydantic Models
class ParticipantActivityBase(DispatchBase):
    plugin_event: PluginEventRead
    started_at: datetime | None
    ended_at: datetime | None
    participant: ParticipantRead
    incident: IncidentRead | None
    case: CaseRead | None


class ParticipantActivityRead(ParticipantActivityBase):
    id: PrimaryKey


class ParticipantActivityCreate(ParticipantActivityBase):
    pass


class ParticipantActivityUpdate(ParticipantActivityBase):
    id: PrimaryKey
