from typing import Optional
from jinja2 import Template

from pydantic import validator, Field
from sqlalchemy import Column, Integer, String, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import INCIDENT_CONFERENCE_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin


class Conference(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    conference_id = Column(String)
    conference_challenge = Column(String, nullable=False, server_default="N/A")
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))


# Pydantic models...
class ConferenceBase(ResourceBase):
    conference_id: Optional[str] = Field(None, nullable=True)
    conference_challenge: Optional[str] = Field(None, nullable=True)


class ConferenceCreate(ConferenceBase):
    pass


class ConferenceUpdate(ConferenceBase):
    pass


class ConferenceRead(ConferenceBase):
    description: Optional[str] = Field(None, nullable=True)

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        return Template(INCIDENT_CONFERENCE_DESCRIPTION).render(
            conference_challenge=values["conference_challenge"]
        )
