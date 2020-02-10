from pydantic import validator

from typing import Optional

from sqlalchemy import Column, Integer

from dispatch.database import Base
from dispatch.messaging import INCIDENT_TICKET_DESCRIPTION
from dispatch.models import DispatchBase, ResourceMixin


class Ticket(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)


# Pydantic models...
class TicketBase(DispatchBase):
    pass


class TicketCreate(TicketBase):
    pass


class TicketUpdate(TicketBase):
    pass


class TicketRead(TicketBase):
    weblink: str
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return INCIDENT_TICKET_DESCRIPTION


class TicketNested(TicketBase):
    id: int
