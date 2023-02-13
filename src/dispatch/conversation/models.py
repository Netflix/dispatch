from pydantic import Field, validator

from typing import Optional

from sqlalchemy import Column, String, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import INCIDENT_CONVERSATION_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin, PrimaryKey


class Conversation(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)
    thread_id = Column(String)

    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class ConversationBase(ResourceBase):
    channel_id: Optional[str] = Field(None, nullable=True)
    thread_id: Optional[str] = Field(None, nullable=True)


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return INCIDENT_CONVERSATION_DESCRIPTION


class ConversationNested(ConversationBase):
    pass
