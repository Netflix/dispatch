from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database import Base
from dispatch.incident.models import IncidentReadNested
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.participant.models import ParticipantRead


class Feedback(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    rating = Column(String)
    feedback = Column(String)

    # Relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))
    participant_id = Column(Integer, ForeignKey("participant.id"))


# Pydantic models
class FeedbackBase(DispatchBase):
    created_at: Optional[datetime]
    rating: str
    feedback: Optional[str]
    incident: Optional[IncidentReadNested]
    participant: Optional[ParticipantRead]


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    id: int


class FeedbackRead(FeedbackBase):
    id: int


class FeedbackPagination(DispatchBase):
    items: List[FeedbackRead]
    total: int
