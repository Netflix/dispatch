from typing import Optional

from .models import Conversation, ConversationCreate


def get_by_channel_id(db_session, channel_id: str) -> Optional[Conversation]:
    """Returns a conversation based on the given channel id."""
    return (
        db_session.query(Conversation).filter(Conversation.channel_id == channel_id).one_or_none()
    )


def get_all(*, db_session):
    """Returns all conversations."""
    return db_session.query(Conversation)


def create(*, db_session, conversation_in: ConversationCreate) -> Conversation:
    """Creates a new conversation."""
    conversation = Conversation(**conversation_in.dict())
    db_session.add(conversation)
    db_session.commit()
    return conversation
