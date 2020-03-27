from typing import Optional

from pydantic import validator
from sqlalchemy import Column, Integer, String

from dispatch.database import Base
from dispatch.messaging import INCIDENT_CONFERENCE_DESCRIPTION
from dispatch.models import DispatchBase, ResourceMixin


class Conference(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    conference_id = Column(String)
    conference_challenge = Column(String, nullable=False, server_default="N/A")


# Pydantic models...
class ConferenceBase(DispatchBase):
    resource_id: str
    resource_type: str
    weblink: str
    conference_id: str
    conference_challenge: str


class ConferenceCreate(ConferenceBase):
    pass


class ConferenceUpdate(ConferenceBase):
    pass


class ConferenceRead(ConferenceBase):
    weblink: str
    conference_challenge: str
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return INCIDENT_CONFERENCE_DESCRIPTION


class ConferenceNested(ConferenceBase):
    pass
