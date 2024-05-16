from datetime import datetime

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
    reminder_at: datetime | None
    individual: IndividualContactRead | None
    project: ProjectRead | None
    schedule_id: str | None
    schedule_name: str | None
    shift_end_at: datetime | None


class ServiceFeedbackReminderCreate(ServiceFeedbackReminderBase):
    pass


class ServiceFeedbackReminderUpdate(ServiceFeedbackReminderBase):
    id: PrimaryKey = None
    reminder_at: datetime | None


class ServiceFeedbackReminderRead(ServiceFeedbackReminderBase):
    id: PrimaryKey
