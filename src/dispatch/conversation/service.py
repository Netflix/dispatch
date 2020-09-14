from typing import Optional

from fastapi.encoders import jsonable_encoder

from dispatch.event import service as event_service

from .models import Conversation, ConversationCreate, ConversationUpdate


def get(*, db_session, conversation_id: int) -> Optional[Conversation]:
    """Fetch a conversation by its `conversation_id`."""
    return db_session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()


def get_by_channel_id(db_session, channel_id: str) -> Optional[Conversation]:
    """Fetch a conversation by its `channel_id`."""
    return (
        db_session.query(Conversation).filter(Conversation.channel_id == channel_id).one_or_none()
    )


def get_by_channel_id_ignoring_channel_type(db_session, channel_id: str) -> Optional[Conversation]:
    """Fetch a conversation by its `channel_id` ignoring the channel type
    and update the channel id in the database if the channel type has changed."""
    conversation = (
        db_session.query(Conversation)
        .filter(Conversation.channel_id.contains(channel_id[1:]))
        .one_or_none()
    )

    if conversation:
        if channel_id[0] != conversation.channel_id[0]:
            # The channel type has changed. We update the channel id in the database
            conversation_in = ConversationUpdate(channel_id=channel_id)
            update(
                db_session=db_session, conversation=conversation, conversation_in=conversation_in,
            )

            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Slack conversation type has changed ({channel_id[0]} -> {conversation.channel_id[0]})",
                incident_id=conversation.incident_id,
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
