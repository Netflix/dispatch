from pydantic import Field

from typing import Optional

from sqlalchemy import Column, String, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.models import ResourceBase, ResourceMixin


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
    description: Optional[str] = Field(None, nullable=True)


class ConversationNested(ConversationBase):
    pass
