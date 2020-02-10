from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from dispatch.database import Base
from dispatch.models import DispatchBase


class ParticipantRoleType(str, Enum):
    incident_commander = "Incident Commander"
    scribe = "Scribe"
    liaison = "Liaison"
    participant = "Participant"
    reporter = "Reporter"


class ParticipantRole(Base):
    id = Column(Integer, primary_key=True)
    assume_at = Column(DateTime, default=datetime.utcnow)
    renounce_at = Column(DateTime)
    role = Column(String, default=ParticipantRoleType.participant)
    participant_id = Column(Integer, ForeignKey("participant.id"))


# Pydantic models...
class ParticipantRoleBase(DispatchBase):
    role: ParticipantRoleType


class ParticipantRoleCreate(ParticipantRoleBase):
    pass


class ParticipantRoleUpdate(ParticipantRoleBase):
    pass


class ParticipantRoleRead(ParticipantRoleBase):
    id: int
    assume_at: Optional[datetime] = None
    renounce_at: Optional[datetime] = None


class ParticipantRolePagination(ParticipantRoleBase):
    total: int
    items: List[ParticipantRoleRead] = []
