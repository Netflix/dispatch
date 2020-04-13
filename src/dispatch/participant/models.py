from datetime import datetime

from typing import Optional, List

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, DateTime, event

from dispatch.database import Base
from dispatch.models import DispatchBase, IndividualReadNested
from dispatch.participant_role.models import ParticipantRoleCreate, ParticipantRoleRead


class Participant(Base):
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    active_at = Column(DateTime, default=datetime.utcnow)
    inactive_at = Column(DateTime)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))
    location = Column(String)
    team = Column(String)
    department = Column(String)
    participant_role = relationship("ParticipantRole", lazy="subquery", backref="participant")
    status_reports = relationship("StatusReport", backref="participant")

    @staticmethod
    def _active_at(mapper, connection, target):
        if target.is_active:
            target.inactive_at = None

    @staticmethod
    def _inactive_at(mapper, connection, target):
        if not target.is_active:
            target.inactive_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._active_at)
        event.listen(cls, "before_update", cls._inactive_at)


class ParticipantBase(DispatchBase):
    location: Optional[str]
    team: Optional[str]
    department: Optional[str]


class ParticipantCreate(ParticipantBase):
    participant_role: Optional[List[ParticipantRoleCreate]] = []


class ParticipantUpdate(ParticipantBase):
    pass


class ParticipantRead(ParticipantBase):
    id: int
    participant_role: Optional[ParticipantRoleRead]
    individual: Optional[IndividualReadNested]
    active_at: Optional[datetime] = None
    inactive_at: Optional[datetime] = None


class ParticipantPagination(DispatchBase):
    total: int
    items: List[ParticipantRead] = []
