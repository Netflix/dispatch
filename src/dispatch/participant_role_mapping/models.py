from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Column, Integer, String, PrimaryKeyConstraint, Table, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.models import PrimaryKey
from dispatch.project.models import ProjectRead

from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin

assoc_participant_roles_tags = Table(
    "participant_role_mapping_tag",
    Base.metadata,
    Column("participant_role_mapping_id", Integer, ForeignKey("participant_role_mapping.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
    PrimaryKeyConstraint("participant_role_mapping_id", "tag_id"),
)

assoc_participant_roles_incident_types = Table(
    "participant_role_mapping_incident_type",
    Base.metadata,
    Column("participant_role_mapping_id", Integer, ForeignKey("participant_role_mapping.id")),
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    PrimaryKeyConstraint("participant_role_mapping_id", "incident_type_id"),
)

assoc_participant_roles_incident_priorities = Table(
    "participant_role_mapping_incident_priority",
    Base.metadata,
    Column("participant_role_mapping_id", Integer, ForeignKey("participant_role_mapping.id")),
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    PrimaryKeyConstraint("participant_role_mapping_id", "incident_priority_id"),
)


class ParticipantRoleMapping(Base, TimeStampMixin, ProjectMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    role = Column(String)
    enabled = Column(Boolean, default=True)

    # Relationships
    tags = relationship("Tag", secondary=assoc_participant_roles_tags)
    incident_types = relationship("IncidentType", secondary=assoc_participant_roles_incident_types)
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_participant_roles_incident_priorities
    )

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service")
    individual_id = Column(Integer, ForeignKey("individual_contact.id"))
    individual = relationship("IndividualContact")


# TODO: ensure that we can only set one target
# def ensure_only_one_target(target, value, oldvalue, initiator):
#    if value:


# listen(ParticipantRoleMapping.service_id, "set", ensure_only_one_target)
# listen(ParticipantRoleMapping.individual_id, "set", ensure_only_one_target)


# Pydantic models
class ParticipantRoleMappingBase(DispatchBase):
    target: str
    enabled: Optional[bool]


class ParticipantRoleMappingCreate(ParticipantRoleMappingBase):
    project: ProjectRead


class ParticipantRoleMappingUpdate(ParticipantRoleMappingBase):
    pass


class ParticipantRoleMappingRead(ParticipantRoleMappingBase):
    id: PrimaryKey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ParticipantRoleMappingPagination(DispatchBase):
    total: int
    items: List[ParticipantRoleMappingRead] = []
