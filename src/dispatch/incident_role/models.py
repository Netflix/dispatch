from datetime import datetime
from typing import Optional, List
from pydantic.types import PositiveInt

from sqlalchemy import Boolean, Column, Integer, String, PrimaryKeyConstraint, Table, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.incident.priority.models import IncidentPriorityRead
from dispatch.incident.type.models import IncidentTypeRead
from dispatch.individual.models import IndividualContactRead
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin
from dispatch.models import PrimaryKey
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.project.models import ProjectRead
from dispatch.service.models import ServiceRead
from dispatch.tag.models import TagRead

assoc_incident_roles_tags = Table(
    "incident_role_tag",
    Base.metadata,
    Column("incident_role_id", Integer, ForeignKey("incident_role.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
    PrimaryKeyConstraint("incident_role_id", "tag_id"),
)

assoc_incident_roles_incident_types = Table(
    "incident_role_incident_type",
    Base.metadata,
    Column("incident_role_id", Integer, ForeignKey("incident_role.id")),
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    PrimaryKeyConstraint("incident_role_id", "incident_type_id"),
)

assoc_incident_roles_incident_priorities = Table(
    "incident_role_incident_priority",
    Base.metadata,
    Column("incident_role_id", Integer, ForeignKey("incident_role.id")),
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    PrimaryKeyConstraint("incident_role_id", "incident_priority_id"),
)


class IncidentRole(Base, TimeStampMixin, ProjectMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    role = Column(String)
    enabled = Column(Boolean, default=True)
    order = Column(Integer)

    # Relationships
    tags = relationship("Tag", secondary=assoc_incident_roles_tags)
    incident_types = relationship("IncidentType", secondary=assoc_incident_roles_incident_types)
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_incident_roles_incident_priorities
    )

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service")
    individual_id = Column(Integer, ForeignKey("individual_contact.id"))
    individual = relationship("IndividualContact")

    engage_next_oncall = Column(Boolean, default=False)


# Pydantic models
class IncidentRoleBase(DispatchBase):
    enabled: Optional[bool]
    tags: Optional[List[TagRead]]
    order: Optional[PositiveInt]
    incident_types: Optional[List[IncidentTypeRead]]
    incident_priorities: Optional[List[IncidentPriorityRead]]
    service: Optional[ServiceRead]
    individual: Optional[IndividualContactRead]
    engage_next_oncall: Optional[bool]


class IncidentRoleCreateUpdate(IncidentRoleBase):
    id: Optional[PrimaryKey]
    project: Optional[ProjectRead]


class IncidentRolesCreateUpdate(DispatchBase):
    policies: List[IncidentRoleCreateUpdate]


class IncidentRoleRead(IncidentRoleBase):
    id: PrimaryKey
    role: ParticipantRoleType
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IncidentRoles(DispatchBase):
    policies: List[IncidentRoleRead] = []
