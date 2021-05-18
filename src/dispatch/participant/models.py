from datetime import datetime

from typing import Optional, List

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, select
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
    team = Column(String)
    department = Column(String)
    location = Column(String)
    added_by_id = Column(Integer, ForeignKey("participant.id"))
    added_by = relationship(
        "Participant", backref=backref("added_participant"), remote_side=[id], post_update=True
    )
    added_reason = Column(String)
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
    def active_roles(self):
        roles = []
        if self.participant_roles:
            for pr in self.participant_roles:
                if not pr.renounced_at:
                    roles.append(pr)
        return roles

    @active_roles.expression
    def active_roles(cls):
        return (
            select([Participant])
            .where(Participant.incident_id == cls.id)
            .where(ParticipantRole.renounced_at == None)  # noqa
        )


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


class ParticipantPagination(DispatchBase):
    total: int
    items: List[ParticipantRead] = []
