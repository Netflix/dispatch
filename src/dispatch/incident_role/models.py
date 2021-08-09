from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Column, Integer, String, PrimaryKeyConstraint, Table, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.models import PrimaryKey
from dispatch.project.models import ProjectRead
from dispatch.tag.models import TagRead
from dispatch.incident_priority.models import IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeRead
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.individual.models import IndividualContactRead
from dispatch.service.models import ServiceRead

from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin

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


# Pydantic models
class IncidentRoleBase(DispatchBase):
    target: str
    role: ParticipantRoleType
    enabled: Optional[bool]
    tags: Optional[List[TagRead]]
    incident_types: Optional[List[IncidentTypeRead]]
    incident_priorities: Optional[List[IncidentPriorityRead]]
    service: Optional[ServiceRead]
    individual: Optional[IndividualContactRead]


class IncidentRoleCreate(IncidentRoleBase):
    project: ProjectRead


class IncidentRoleUpdate(IncidentRoleBase):
    pass


class IncidentRoleRead(IncidentRoleBase):
    id: PrimaryKey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IncidentRolePagination(DispatchBase):
    total: int
    items: List[IncidentRoleRead] = []
