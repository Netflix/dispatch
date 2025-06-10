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


def test_get_by_channel_id_ignoring_channel_type_no_conversations(session):
    """Test when no conversations match the channel_id."""
    from dispatch.conversation.service import get_by_channel_id_ignoring_channel_type

    result = get_by_channel_id_ignoring_channel_type(
        db_session=session, channel_id="nonexistent_channel"
    )
    assert result is None


def test_get_by_channel_id_ignoring_channel_type_single_conversation(session):
    """Test when exactly one conversation matches the channel_id."""
    from dispatch.conversation.service import create, get_by_channel_id_ignoring_channel_type
    from dispatch.conversation.models import ConversationCreate

    # Create a single conversation
    conversation_in = ConversationCreate(
        channel_id="test_channel",
        resource_id="test_resource",
        resource_type="test_type",
        weblink="https://example.com/",
    )
    created_conversation = create(db_session=session, conversation_in=conversation_in)

    # Test retrieval
    result = get_by_channel_id_ignoring_channel_type(db_session=session, channel_id="test_channel")

    assert result is not None
    assert result.id == created_conversation.id
    assert result.channel_id == "test_channel"


def test_get_by_channel_id_ignoring_channel_type_multiple_conversations_warning(session, caplog):
    """Test when multiple conversations match the channel_id with thread_id=None - should return first conversation."""
    from dispatch.conversation.service import create, get_by_channel_id_ignoring_channel_type
    from dispatch.conversation.models import ConversationCreate

    # Create multiple conversations with the same channel_id
    conversation_in_1 = ConversationCreate(
        channel_id="duplicate_channel",
        resource_id="resource_1",
        resource_type="test_type",
        weblink="https://example1.com/",
    )
    conversation_in_2 = ConversationCreate(
        channel_id="duplicate_channel",
        resource_id="resource_2",
        resource_type="test_type",
        weblink="https://example2.com/",
    )

    created_1 = create(db_session=session, conversation_in=conversation_in_1)
    create(db_session=session, conversation_in=conversation_in_2)

    # Test retrieval - should return first conversation when thread_id is None
    result = get_by_channel_id_ignoring_channel_type(
        db_session=session, channel_id="duplicate_channel"
    )

    # When thread_id is None, it uses .first() so should return the first conversation
    assert result is not None
    assert result.id == created_1.id


def test_get_by_channel_id_ignoring_channel_type_multiple_conversations_fallback_warning(
    session, caplog
):
    """Test when multiple conversations match in fallback logic - should log warning and return None."""
    from dispatch.conversation.service import create, get_by_channel_id_ignoring_channel_type
    from dispatch.conversation.models import ConversationCreate

    # Create multiple conversations with the same channel_id but no thread_id
    conversation_in_1 = ConversationCreate(
        channel_id="fallback_channel",
        resource_id="resource_1",
        resource_type="test_type",
        weblink="https://example1.com/",
    )
    conversation_in_2 = ConversationCreate(
        channel_id="fallback_channel",
        resource_id="resource_2",
        resource_type="test_type",
        weblink="https://example2.com/",
    )

    create(db_session=session, conversation_in=conversation_in_1)
    create(db_session=session, conversation_in=conversation_in_2)

    # Test retrieval with a thread_id that doesn't exist - should trigger fallback logic
    result = get_by_channel_id_ignoring_channel_type(
        db_session=session, channel_id="fallback_channel", thread_id="nonexistent_thread"
    )

    # Should return None and log warning in fallback logic
    assert result is None
    assert (
        "Multiple conversations found for channel_id: fallback_channel, thread_id: nonexistent_thread"
        in caplog.text
    )


def test_get_by_channel_id_ignoring_channel_type_with_thread_id(session):
    """Test the thread_id matching logic."""
    from dispatch.conversation.service import create, get_by_channel_id_ignoring_channel_type
    from dispatch.conversation.models import ConversationCreate

    # Create conversations with different thread_ids
    conversation_in_1 = ConversationCreate(
        channel_id="thread_channel",
        thread_id="thread_123",
        resource_id="resource_1",
        resource_type="test_type",
        weblink="https://example1.com/",
    )
    conversation_in_2 = ConversationCreate(
        channel_id="thread_channel",
        thread_id="thread_456",
        resource_id="resource_2",
        resource_type="test_type",
        weblink="https://example2.com/",
    )

    created_1 = create(db_session=session, conversation_in=conversation_in_1)
    create(db_session=session, conversation_in=conversation_in_2)

    # Test retrieval with specific thread_id
    result = get_by_channel_id_ignoring_channel_type(
        db_session=session, channel_id="thread_channel", thread_id="thread_123"
    )

    assert result is not None
    assert result.id == created_1.id
    assert result.thread_id == "thread_123"


def test_get_by_channel_id_ignoring_channel_type_incident_message_fallback(session):
    """Test the incident message fallback logic (no thread_id provided)."""
    from dispatch.conversation.service import create, get_by_channel_id_ignoring_channel_type
    from dispatch.conversation.models import ConversationCreate

    # Create a conversation without thread_id (incident message)
    conversation_in = ConversationCreate(
        channel_id="incident_channel",
        resource_id="incident_resource",
        resource_type="test_type",
        weblink="https://example.com/",
    )
    created_conversation = create(db_session=session, conversation_in=conversation_in)

    # Test retrieval without thread_id - should use .first()
    result = get_by_channel_id_ignoring_channel_type(
        db_session=session, channel_id="incident_channel"
    )

    assert result is not None
    assert result.id == created_conversation.id
