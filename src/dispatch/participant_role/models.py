from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from dispatch.database.core import Base
from dispatch.models import DispatchBase


class ParticipantRoleType(str, Enum):
    incident_commander = "Incident Commander"
    scribe = "Scribe"
    liaison = "Liaison"
    participant = "Participant"
    reporter = "Reporter"


class ParticipantRole(Base):
    id = Column(Integer, primary_key=True)
    assumed_at = Column(DateTime, default=datetime.utcnow)
    renounced_at = Column(DateTime)
    role = Column(String, default=ParticipantRoleType.participant.value)
    participant_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))


# Pydantic models...
class ParticipantRoleBase(DispatchBase):
    role: str


class ParticipantRoleCreate(ParticipantRoleBase):
    role: Optional[ParticipantRoleType]


class ParticipantRoleUpdate(ParticipantRoleBase):
    pass


class ParticipantRoleRead(ParticipantRoleBase):
    id: int
    assumed_at: Optional[datetime] = None
    renounced_at: Optional[datetime] = None


class ParticipantRolePagination(ParticipantRoleBase):
    total: int
    items: List[ParticipantRoleRead] = []
