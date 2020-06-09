from datetime import datetime

from typing import Optional, List

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, DateTime, event

from dispatch.database import Base
from dispatch.models import DispatchBase, IndividualReadNested
from dispatch.participant_role.models import ParticipantRoleCreate, ParticipantRoleRead


class Participant(Base):
    # columns
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)  # TODO(mvilanova): make it a hybrid property
    active_at = Column(
        DateTime, default=datetime.utcnow
    )  # TODO(mvilanova): make it a hybrid property
    inactive_at = Column(DateTime)  # TODO(mvilanova): make it a hybrid property
    team = Column(String)
    department = Column(String)
    invited_by = relationship("Participant", backref=backref("invited"), remote_side=[id])
    invite_reason = Column(String)
    location = Column(String)
    after_hours_notification = Column(Boolean, default=False)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))
    participant_roles = relationship("ParticipantRole", backref="participant")
    reports = relationship("Report", backref="participant")

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
    participant_roles: Optional[List[ParticipantRoleCreate]] = []
    location: Optional[str]
    team: Optional[str]
    department: Optional[str]


class ParticipantUpdate(ParticipantBase):
    pass


class ParticipantRead(ParticipantBase):
    id: int
    participant_roles: Optional[List[ParticipantRoleRead]] = []
    individual: Optional[IndividualReadNested]
    active_at: Optional[datetime] = None
    inactive_at: Optional[datetime] = None


class ParticipantPagination(DispatchBase):
    total: int
    items: List[ParticipantRead] = []
