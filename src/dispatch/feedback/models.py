from datetime import datetime
from pydantic import Field
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType


from dispatch.database.core import Base
from dispatch.feedback.enums import FeedbackRating
from dispatch.incident.models import IncidentReadNested
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey
from dispatch.participant.models import ParticipantRead


class Feedback(TimeStampMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    rating = Column(String)
    feedback = Column(String)

    # Relationships
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    participant_id = Column(Integer, ForeignKey("participant.id"))

    search_vector = Column(TSVectorType("feedback", "rating"))

    @hybrid_property
    def project(self):
        return self.incident.project


# Pydantic models
class FeedbackBase(DispatchBase):
    created_at: Optional[datetime]
    rating: FeedbackRating = FeedbackRating.very_satisfied
    feedback: Optional[str] = Field(None, nullable=True)
    incident: Optional[IncidentReadNested]
    participant: Optional[ParticipantRead]


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    id: PrimaryKey = None


class FeedbackRead(FeedbackBase):
    id: PrimaryKey


class FeedbackPagination(DispatchBase):
    items: List[FeedbackRead]
    total: int
