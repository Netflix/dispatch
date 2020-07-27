from pydantic import validator

from typing import Optional

from sqlalchemy import Column, String, Integer

from dispatch.database import Base
from dispatch.messaging import INCIDENT_CONVERSATION_DESCRIPTION
from dispatch.models import DispatchBase, ResourceMixin


class Conversation(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)


# Pydantic models...
class ConversationBase(DispatchBase):
    resource_id: Optional[str]
    resource_type: Optional[str]
    weblink: Optional[str]
    channel_id: Optional[str]


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return INCIDENT_CONVERSATION_DESCRIPTION


class ConversationNested(ConversationBase):
    pass
