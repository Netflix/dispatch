"""Models for conversation resources in the Dispatch application."""

from pydantic import field_validator

from sqlalchemy import Column, String, Integer, ForeignKey

from dispatch.database.core import Base
from dispatch.messaging.strings import INCIDENT_CONVERSATION_DESCRIPTION
from dispatch.models import ResourceBase, ResourceMixin, PrimaryKey


class Conversation(Base, ResourceMixin):
    """SQLAlchemy model for conversation resources."""
    id = Column(Integer, primary_key=True)
    channel_id = Column(String)
    thread_id = Column(String)

    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))


# Pydantic models...
class ConversationBase(ResourceBase):
    """Base Pydantic model for conversation resources."""
    channel_id: str | None = None
    thread_id: str | None = None


class ConversationCreate(ConversationBase):
    """Pydantic model for creating a conversation resource."""
    pass


class ConversationUpdate(ConversationBase):
    """Pydantic model for updating a conversation resource."""
    pass


class ConversationRead(ConversationBase):
    """Pydantic model for reading a conversation resource."""
    id: PrimaryKey
    description: str | None = None

    @field_validator("description", mode="before")
    @classmethod
    def set_description(cls, _):
        """Sets the description for the conversation resource."""
        return INCIDENT_CONVERSATION_DESCRIPTION


class ConversationNested(ConversationBase):
    """Pydantic model for a nested conversation resource."""
    pass
