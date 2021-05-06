from datetime import datetime

from typing import Optional, List

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, DateTime, event, select
from sqlalchemy.ext.hybrid import hybrid_property

from dispatch.database.core import Base
from dispatch.models import DispatchBase, IndividualReadNested
from dispatch.participant_role.models import (
    ParticipantRoleCreate,
    ParticipantRoleRead,
    ParticipantRole,
)
from dispatch.service.models import ServiceRead


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
    added_by_id = Column(Integer, ForeignKey("participant.id"))
    added_by = relationship(
        "Participant", backref=backref("added_participant"), remote_side=[id], post_update=True
    )
    added_reason = Column(String)
    location = Column(String)
    after_hours_notification = Column(Boolean, default=False)

    # relationships
    feedback = relationship("Feedback", backref="participant")
    service_id = Column(Integer, ForeignKey("service.id", ondelete="CASCADE"))
    service = relationship("Service", backref="participant")
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    individual = relationship("IndividualContact", lazy="subquery", backref="participant")
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))
    participant_roles = relationship(
        "ParticipantRole", backref="participant", lazy="subquery", cascade="all, delete-orphan"
    )
    reports = relationship("Report", backref="participant")
    created_tasks = relationship(
        "Task", backref="creator", primaryjoin="Participant.id==Task.creator_id"
    )
    owned_tasks = relationship("Task", backref="owner", primaryjoin="Participant.id==Task.owner_id")

    @hybrid_property
    def current_roles(self):
        roles = []
        if self.participant_roles:
            for pr in self.participant_roles:
                if not pr.renounced_at:
                    roles.append(pr)
        return roles

    @current_roles.expression
    def current_roles(cls):
        return (
            select([Participant])
            .where(Participant.incident_id == cls.id)
            .where(ParticipantRole.renounced_at == None)  # noqa
        )

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
    added_reason: Optional[str]


class ParticipantCreate(ParticipantBase):
    participant_roles: Optional[List[ParticipantRoleCreate]] = []
    location: Optional[str]
    team: Optional[str]
    department: Optional[str]
    service: Optional[ServiceRead]


class ParticipantUpdate(ParticipantBase):
    individual: Optional[IndividualReadNested]


class ParticipantRead(ParticipantBase):
    id: int
    participant_roles: Optional[List[ParticipantRoleRead]] = []
    individual: Optional[IndividualReadNested]
    active_at: Optional[datetime] = None
    inactive_at: Optional[datetime] = None


class ParticipantPagination(DispatchBase):
    total: int
    items: List[ParticipantRead] = []
