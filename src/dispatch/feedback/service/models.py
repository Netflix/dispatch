from datetime import datetime
from pydantic import Field

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric, JSON
from sqlalchemy_utils import TSVectorType
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.models import DispatchBase, TimeStampMixin, FeedbackMixin, PrimaryKey, Pagination
from dispatch.project.models import ProjectRead

from .enums import ServiceFeedbackRating


class ServiceFeedback(TimeStampMixin, FeedbackMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    schedule = Column(String)
    hours = Column(Numeric(precision=10, scale=2))
    shift_start_at = Column(DateTime)
    shift_end_at = Column(DateTime)
    details = Column(JSON)

    # Relationships
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project")

    search_vector = Column(
        TSVectorType(
            "feedback",
            "rating",
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models
class ServiceFeedbackBase(DispatchBase):
    feedback: str | None = None
    hours: float | None = None
    individual: IndividualContactReadMinimal | None = None
    rating: ServiceFeedbackRating = ServiceFeedbackRating.little_effort
    schedule: str | None = None
    shift_end_at: datetime | None = None
    shift_start_at: datetime | None = None
    project: ProjectRead | None = None
    created_at: datetime | None = None
    details: list[dict | None] = Field([], nullable=True)


class ServiceFeedbackCreate(ServiceFeedbackBase):
    pass


class ServiceFeedbackUpdate(ServiceFeedbackBase):
    id: PrimaryKey = None


class ServiceFeedbackRead(ServiceFeedbackBase):
    id: PrimaryKey
    project: ProjectRead | None = None


class ServiceFeedbackPagination(Pagination):
    items: list[ServiceFeedbackRead]
    total: int
