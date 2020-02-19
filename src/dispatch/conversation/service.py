from typing import Optional

from fastapi.encoders import jsonable_encoder

from .models import Conversation, ConversationCreate, ConversationUpdate


def get(*, db_session, conversation_id: int) -> Optional[Conversation]:
    """Returns a conversation based on the given conversation id."""
    return db_session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()


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


def update(
    *, db_session, conversation: Conversation, conversation_in: ConversationUpdate
) -> Conversation:
    """Updates a conversation."""
    conversation_data = jsonable_encoder(conversation)
    update_data = conversation_in.dict(skip_defaults=True)

    for field in conversation_data:
        if field in update_data:
            setattr(conversation, field, update_data[field])

    db_session.add(conversation)
    db_session.commit()
    return conversation


def delete(*, db_session, conversation_id: int):
    """Deletes a conversation."""
    db_session.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db_session.commit()
