from datetime import datetime
from pydantic import Field
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.models import IncidentReadMinimal
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey
from dispatch.participant.models import ParticipantRead
from dispatch.project.models import ProjectRead

from .enums import ServiceFeedbackRating


class ServiceFeedback(TimeStampMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    rating = Column(String)
    feedback = Column(String)

    # Relationships
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    participant_id = Column(Integer, ForeignKey("participant.id"))

    search_vector = Column(
        TSVectorType(
            "feedback",
            "rating",
            regconfig="pg_catalog.simple",
        )
    )

    @hybrid_property
    def project(self):
        return self.incident.project


# Pydantic models
class ServiceFeedbackBase(DispatchBase):
    created_at: Optional[datetime]
    rating: ServiceFeedbackRating = ServiceFeedbackRating.extreme_effort
    feedback: Optional[str] = Field(None, nullable=True)
    incident: Optional[IncidentReadMinimal]
    participant: Optional[ParticipantRead]


class ServiceFeedbackCreate(ServiceFeedbackBase):
    pass


class ServiceFeedbackUpdate(ServiceFeedbackBase):
    id: PrimaryKey = None


class ServiceFeedbackRead(ServiceFeedbackBase):
    id: PrimaryKey
    project: Optional[ProjectRead]


class ServiceFeedbackPagination(DispatchBase):
    items: List[ServiceFeedbackRead]
    total: int
