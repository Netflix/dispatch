from typing import List, Optional

from pydantic import validator
from sqlalchemy import Boolean, Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship

from dispatch.database.base import Base
from dispatch.incident_priority.models import IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeRead
from dispatch.models import (
    DispatchBase,
    IndividualReadNested,
    ServiceReadNested,
    TeamReadNested,
)
from dispatch.document.models import DocumentRead
from dispatch.term.models import TermRead

recommendation_documents = Table(
    "recommendation_documents",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("document_id", "recommendation_id"),
)

recommendation_terms = Table(
    "recommendation_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("term_id", "recommendation_id"),
)

recommendation_services = Table(
    "recommendation_services",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("service_id", "recommendation_id"),
)

recommendation_individual_contacts = Table(
    "recommendation_individual_contacts",
    Base.metadata,
    Column("individual_contact_id", Integer, ForeignKey("individual_contact.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("individual_contact_id", "recommendation_id"),
)

recommendation_team_contacts = Table(
    "recommendation_team_contacts",
    Base.metadata,
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("team_contact_id", "recommendation_id"),
)

recommendation_incident_types = Table(
    "recommendation_incident_types",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("incident_type_id", "recommendation_id"),
)

recommendation_incident_priorities = Table(
    "recommendation_incident_priorities",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("recommendation_id", Integer, ForeignKey("recommendation.id")),
    PrimaryKeyConstraint("incident_priority_id", "recommendation_id"),
)


class RecommendationAccuracy(Base):
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation.id"))
    correct = Column(Boolean)
    resource_id = Column(Integer)
    resource_type = Column(String)


class Recommendation(Base):
    id = Column(Integer, primary_key=True)
    text = Column(String)
    matched_terms = relationship("Term", secondary=recommendation_terms, backref="recommendations")
    accuracy = relationship("RecommendationAccuracy")

    documents = relationship(
        "Document", secondary=recommendation_documents, backref="recommendations"
    )
    team_contacts = relationship(
        "TeamContact", secondary=recommendation_team_contacts, backref="recommendations"
    )
    individual_contacts = relationship(
        "IndividualContact", secondary=recommendation_individual_contacts, backref="recommendations"
    )
    service_contacts = relationship(
        "Service", secondary=recommendation_services, backref="recommendations"
    )
    incident_types = relationship(
        "IncidentType", secondary=recommendation_incident_types, backref="recommendations"
    )
    incident_priorities = relationship(
        "IncidentPriority", secondary=recommendation_incident_priorities, backref="recommendations"
    )


# Pydantic models...
class RecommendationBase(DispatchBase):
    text: Optional[str]
    matched_terms: Optional[List[TermRead]] = []
    service_contacts: Optional[List[ServiceReadNested]] = []
    team_contacts: Optional[List[TeamReadNested]] = []
    documents: Optional[List[DocumentRead]] = []
    individual_contacts: Optional[List[IndividualReadNested]] = []
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []


class ContextBase(DispatchBase):
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    terms: Optional[List[TermRead]] = []


class RouteBase(DispatchBase):
    text: Optional[str]
    context: Optional[ContextBase]

    # NOTE order matters here to validate multiple arguments we must only validate the last one.
    @validator("context")
    def check_text_or_context(cls, v, values):  # pylint: disable=no-self-argument
        if "text" not in values and "context" not in values:
            raise ValueError("Either 'text' or 'context' must be passed")
        return v


class RouteRequest(RouteBase):
    pass


class RouteResponse(RouteBase):
    recommendation: RecommendationBase
