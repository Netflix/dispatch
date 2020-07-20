from typing import Optional
from jinja2 import Template

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
    resource_id: Optional[str]
    resource_type: Optional[str]
    weblink: Optional[str]
    conference_id: Optional[str]
    conference_challenge: Optional[str]


class ConferenceCreate(ConferenceBase):
    pass


class ConferenceUpdate(ConferenceBase):
    pass


class ConferenceRead(ConferenceBase):
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        return Template(INCIDENT_CONFERENCE_DESCRIPTION).render(
            conference_challenge=values["conference_challenge"]
        )


class ConferenceNested(ConferenceBase):
    pass
