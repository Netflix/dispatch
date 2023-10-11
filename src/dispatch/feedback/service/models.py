from datetime import datetime
from pydantic import Field
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Numeric
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
    feedback: Optional[str] = Field(None, nullable=True)
    hours: Optional[float]
    individual: Optional[IndividualContactReadMinimal]
    rating: ServiceFeedbackRating = ServiceFeedbackRating.little_effort
    schedule: Optional[str]
    shift_end_at: Optional[datetime]
    shift_start_at: Optional[datetime]
    project: Optional[ProjectRead]
    created_at: Optional[datetime]


class ServiceFeedbackCreate(ServiceFeedbackBase):
    pass


class ServiceFeedbackUpdate(ServiceFeedbackBase):
    id: PrimaryKey = None


class ServiceFeedbackRead(ServiceFeedbackBase):
    id: PrimaryKey
    project: Optional[ProjectRead]


class ServiceFeedbackPagination(Pagination):
    items: List[ServiceFeedbackRead]
    total: int
