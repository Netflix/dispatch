import pytest


def test_get_by_channel_id(session, conversation):
    from dispatch.conversation.service import get_by_channel_id

    t_conversation = get_by_channel_id(db_session=session, channel_id=conversation.channel_id)
    assert t_conversation.channel_id == conversation.channel_id


def test_get_all(session, conversation):
    from dispatch.conversation.service import get_all

    t_conversations = get_all(db_session=session).all()
    assert len(t_conversations) > 1


def test_create(session):
    from dispatch.conversation.service import create
    from dispatch.conversation.models import ConversationCreate

    channel_id = "XXX"
    resource_id = "XXX"
    resource_type = "XXX"
    weblink = "https://example.com/"

    conversation_in = ConversationCreate(
        channel_id=channel_id, resource_id=resource_id, resource_type=resource_type, weblink=weblink
    )
    conversation = create(db_session=session, conversation_in=conversation_in)
    assert conversation
