from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.incident_priority.models import IncidentPriorityCreate, IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead
from dispatch.term.models import TermCreate
from dispatch.models import ContactBase, ContactMixin, DispatchBase, TermReadNested

# Association tables for many to many relationships
assoc_individual_contact_incident_types = Table(
    "assoc_individual_contact_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("individual_contact_id", Integer, ForeignKey("individual_contact.id")),
    PrimaryKeyConstraint("incident_type_id", "individual_contact_id"),
)

assoc_individual_contact_incident_priorities = Table(
    "assoc_individual_contact_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("individual_contact_id", Integer, ForeignKey("individual_contact.id")),
    PrimaryKeyConstraint("incident_priority_id", "individual_contact_id"),
)

assoc_individual_contact_terms = Table(
    "assoc_individual_contact_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("individual_contact_id", ForeignKey("individual_contact.id")),
    PrimaryKeyConstraint("term_id", "individual_contact_id"),
)


class IndividualContact(ContactMixin, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    mobile_phone = Column(String)
    office_phone = Column(String)
    title = Column(String)
    weblink = Column(String)

    # this is a self referential relationship lets punt on this for now.
    # relationship_owner_id = Column(Integer, ForeignKey("individual_contact.id"))
    # relationship_owner = relationship("IndividualContact", backref="individual_contacts")
    events = relationship("Event", backref="individual")
    incident_types = relationship(
        "IncidentType", secondary=assoc_individual_contact_incident_types, backref="individuals"
    )
    incident_priorities = relationship(
        "IncidentPriority",
        secondary=assoc_individual_contact_incident_priorities,
        backref="individuals",
    )
    # participant = relationship("Participant", lazy="subquery", backref="individual")
    team_contact_id = Column(Integer, ForeignKey("team_contact.id"))
    team_contact = relationship("TeamContact", backref="individuals")
    terms = relationship("Term", secondary=assoc_individual_contact_terms, backref="individuals")

    search_vector = Column(
        TSVectorType(
            "name",
            "title",
            "company",
            "notes",
            weights={"name": "A", "title": "B", "company": "C", "notes": "D"},
        )
    )


class IndividualContactBase(ContactBase):
    weblink: Optional[str]
    mobile_phone: Optional[str]
    office_phone: Optional[str]
    title: Optional[str]


class IndividualContactCreate(IndividualContactBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class IndividualContactUpdate(IndividualContactBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class IndividualContactRead(IndividualContactBase):
    id: int
    terms: Optional[List[TermReadNested]] = []
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IndividualContactPagination(DispatchBase):
    total: int
    items: List[IndividualContactRead] = []
