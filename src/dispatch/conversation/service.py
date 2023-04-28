from typing import Optional

from .models import Conversation, ConversationCreate, ConversationUpdate


def get(*, db_session, conversation_id: int) -> Optional[Conversation]:
    """Gets a conversation by its id."""
    return db_session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()


def get_by_channel_id_ignoring_channel_type(db_session, channel_id: str) -> Optional[Conversation]:
    """
    Gets a conversation by its id ignoring the channel type, and update the
    channel id in the database if the channel type has changed.
    """
    channel_id_without_type = channel_id[1:]
    conversation = (
        db_session.query(Conversation)
        .filter(Conversation.channel_id.contains(channel_id_without_type))
        .one_or_none()
    )

    if conversation:
        if channel_id[0] != conversation.channel_id[0]:
            # We update the channel id if the channel type has changed (public <-> private)
            conversation_in = ConversationUpdate(channel_id=channel_id)
            update(
                db_session=db_session,
                conversation=conversation,
                conversation_in=conversation_in,
            )

    return conversation


def get_all(*, db_session):
    """Fetches all conversations."""
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
    conversation_data = conversation.dict()
    update_data = conversation_in.dict(skip_defaults=True)

    for field in conversation_data:
        if field in update_data:
            setattr(conversation, field, update_data[field])

    db_session.commit()
    return conversation


def delete(*, db_session, conversation_id: int):
    """Deletes a conversation."""
    db_session.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db_session.commit()
