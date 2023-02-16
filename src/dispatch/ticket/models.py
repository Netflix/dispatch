from pydantic import validator, Field

from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import TICKET_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin


class Ticket(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class TicketBase(ResourceBase):
    pass


class TicketCreate(TicketBase):
    pass


class TicketUpdate(TicketBase):
    pass


class TicketRead(TicketBase):
    description: Optional[str] = Field(None, nullable=True)

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return TICKET_DESCRIPTION
