def test_get(session, conversation):
    from dispatch.conversation.service import get

    t_conversation = get(db_session=session, conversation_id=conversation.id)
    assert t_conversation.id == conversation.id


def test_get_all(session, conversations):
    from dispatch.conversation.service import get_all

    t_conversations = get_all(db_session=session).all()
    assert t_conversations


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


def test_update(session, conversation):
    from dispatch.conversation.service import update
    from dispatch.conversation.models import ConversationUpdate

    channel_id = "channel_id"

    conversation_in = ConversationUpdate(
        channel_id=channel_id,
    )
    conversation = update(
        db_session=session,
        conversation=conversation,
        conversation_in=conversation_in,
    )
    assert conversation.channel_id == channel_id


def test_delete(session, conversation):
    from dispatch.conversation.service import delete, get

    delete(db_session=session, conversation_id=conversation.id)
    assert not get(db_session=session, conversation_id=conversation.id)
