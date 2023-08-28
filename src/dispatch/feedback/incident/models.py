from datetime import datetime
from pydantic import Field
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.models import IncidentReadMinimal
from dispatch.models import DispatchBase, TimeStampMixin, FeedbackMixin, PrimaryKey, Pagination
from dispatch.participant.models import ParticipantRead
from dispatch.project.models import ProjectRead

from .enums import FeedbackRating


class Feedback(TimeStampMixin, FeedbackMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)

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
class FeedbackBase(DispatchBase):
    created_at: Optional[datetime]
    rating: FeedbackRating = FeedbackRating.very_satisfied
    feedback: Optional[str] = Field(None, nullable=True)
    incident: Optional[IncidentReadMinimal]
    participant: Optional[ParticipantRead]


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    id: PrimaryKey = None


class FeedbackRead(FeedbackBase):
    id: PrimaryKey
    project: Optional[ProjectRead]


class FeedbackPagination(Pagination):
    items: List[FeedbackRead]
