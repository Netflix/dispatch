from datetime import datetime
from pydantic import Field

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.models import IncidentReadBasic
from dispatch.models import (
    DispatchBase,
    TimeStampMixin,
    FeedbackMixin,
    PrimaryKey,
    Pagination,
    ProjectMixin,
)
from dispatch.participant.models import ParticipantRead
from dispatch.project.models import ProjectRead
from dispatch.case.models import CaseReadMinimal

from .enums import FeedbackRating


class Feedback(TimeStampMixin, FeedbackMixin, ProjectMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)

    # Relationships
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    participant_id = Column(Integer, ForeignKey("participant.id"))

    search_vector = Column(
        TSVectorType(
            "feedback",
            "rating",
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models
class FeedbackBase(DispatchBase):
    created_at: datetime | None = None
    rating: FeedbackRating = FeedbackRating.very_satisfied
    feedback: str | None = Field(None, nullable=True)
    incident: IncidentReadBasic | None = None
    case: CaseReadMinimal | None = None
    participant: ParticipantRead | None = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    id: PrimaryKey = None


class FeedbackRead(FeedbackBase):
    id: PrimaryKey
    project: ProjectRead | None


class FeedbackPagination(Pagination):
    items: list[FeedbackRead]
