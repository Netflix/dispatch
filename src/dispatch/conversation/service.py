import logging
from .models import Conversation, ConversationCreate, ConversationUpdate

log = logging.getLogger(__name__)


def get(*, db_session, conversation_id: int) -> Conversation | None:
    """Gets a conversation by its id."""
    return db_session.query(Conversation).filter(Conversation.id == conversation_id).one_or_none()


def get_by_channel_id_ignoring_channel_type(
    db_session, channel_id: str, thread_id: str = None
) -> Conversation | None:
    """
    Gets a conversation by its id ignoring the channel type, and updates the
    channel id in the database if the channel type has changed.
    """
    conversation = None

    conversations = db_session.query(Conversation).filter(Conversation.channel_id == channel_id)

    # The code below disambiguates between incident threads, case threads, and incident messages
    if not thread_id:
        # assume incident message
        conversation = conversations.first()

    if not conversation:
        conversation = conversations.filter(Conversation.thread_id == thread_id).one_or_none()

        if not conversation:
            # No conversations with that thread_id, check all conversations without thread filter
            conversation_count = conversations.count()
            if conversation_count > 1:
                log.warning(
                    f"Multiple conversations found for channel_id: {channel_id}, thread_id: {thread_id}"
                )
                conversation = None
            else:
                conversation = conversations.one_or_none()

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
    update_data = conversation_in.dict(exclude_unset=True)

    for field in conversation_data:
        if field in update_data:
            setattr(conversation, field, update_data[field])

    db_session.commit()
    return conversation


def delete(*, db_session, conversation_id: int):
    """Deletes a conversation."""
    db_session.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db_session.commit()
