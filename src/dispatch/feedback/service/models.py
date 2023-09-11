from datetime import datetime
from pydantic import Field
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactRead
from dispatch.models import DispatchBase, TimeStampMixin, FeedbackMixin, PrimaryKey
from dispatch.project.models import ProjectRead
from .reminder.models import ServiceFeedbackReminderRead

from .enums import ServiceFeedbackRating


class ServiceFeedback(TimeStampMixin, FeedbackMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    feedback = Column(String)
    rating = Column(String)
    schedule = Column(String)
    hours = Column(Integer)
    shift_start_at = Column(DateTime)
    shift_end_at = Column(DateTime)

    # Relationships
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))

    search_vector = Column(
        TSVectorType(
            "feedback",
            "rating",
            regconfig="pg_catalog.simple",
        )
    )

    @hybrid_property
    def project(self):
        return self.service.project


# Pydantic models
class ServiceFeedbackBase(DispatchBase):
    feedback: Optional[str] = Field(None, nullable=True)
    hours: Optional[int]
    individual: Optional[IndividualContactRead]
    rating: ServiceFeedbackRating = ServiceFeedbackRating.little_effort
    schedule: Optional[str]
    shift_end_at: Optional[datetime]
    shift_start_at: Optional[datetime]


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
