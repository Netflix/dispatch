from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactRead
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class ServiceFeedbackReminder(TimeStampMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    reminder_at = Column(DateTime)
    schedule_id = Column(String)
    schedule_name = Column(String)
    shift_end_at = Column(DateTime)

    # Relationships
    individual_contact_id = Column(Integer, ForeignKey("individual_contact.id"))
    project_id = Column(Integer, ForeignKey("project.id"))


# Pydantic models
class ServiceFeedbackReminderBase(DispatchBase):
    reminder_at: Optional[datetime]
    individual: Optional[IndividualContactRead]
    project: Optional[ProjectRead]
    schedule_id: Optional[str]
    schedule_name: Optional[str]
    shift_end_at: Optional[datetime]


class ServiceFeedbackReminderCreate(ServiceFeedbackReminderBase):
    pass


class ServiceFeedbackReminderUpdate(ServiceFeedbackReminderBase):
    id: PrimaryKey = None
    reminder_at: Optional[datetime]


class ServiceFeedbackReminderRead(ServiceFeedbackReminderBase):
    id: PrimaryKey
