from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


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
    rating: str
    feedback: Optional[str]


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    id: int


class FeedbackRead(FeedbackBase):
    id: int


class FeedbackPagination(DispatchBase):
    items: List[FeedbackRead]
    total: int
