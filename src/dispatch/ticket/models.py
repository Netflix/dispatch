"""Models for ticket functionality in the Dispatch application."""

from pydantic import field_validator

from sqlalchemy import Column, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import TICKET_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin


class Ticket(Base, ResourceMixin):
    """SQLAlchemy model for ticket resources."""

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))


# Pydantic models...
class TicketBase(ResourceBase):
    """Base Pydantic model for ticket resources."""


class TicketCreate(TicketBase):
    """Pydantic model for creating a ticket resource."""


class TicketUpdate(TicketBase):
    """Pydantic model for updating a ticket resource."""


class TicketRead(TicketBase):
    """Pydantic model for reading a ticket resource."""

    description: str | None = TICKET_DESCRIPTION

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, _v: str | None):
        """Sets the description."""
        return TICKET_DESCRIPTION
