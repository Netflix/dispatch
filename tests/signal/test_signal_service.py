import json


def test_get(session, signal):
    from dispatch.signal.service import get

    t_signal = get(db_session=session, signal_id=signal.id)
    assert t_signal.id == signal.id


def test_create(session, project, case_priority, case_type, service, tag, entity_type):
    from dispatch.signal.models import SignalCreate, Service, TagRead, EntityTypeRead, ProjectRead, CasePriorityRead, CaseTypeRead
    from dispatch.signal.service import create

    name = "name"
    description = "description"
    owner = "example@test.com"
    external_id = "foo"
    external_url = "http://example.com"
    conversation_target = "#general"
    variant = "v1"
    lifecycle = "active"
    runbook = "http://runbook.com"
    genai_model = "gpt-4"
    genai_system_message = "system"
    genai_prompt = "prompt"

    signal_in = SignalCreate(
        name=name,
        owner=owner,
        project=ProjectRead(**project.__dict__),
        case_priority=CasePriorityRead(**case_priority.__dict__),
        case_type=CaseTypeRead(**case_type.__dict__),
        conversation_target=conversation_target,
        external_id=external_id,
        external_url=external_url,
        description=description,
        oncall_service=Service(**service.__dict__),
        source=None,
        variant=variant,
        lifecycle=lifecycle,
        runbook=runbook,
        genai_model=genai_model,
        genai_system_message=genai_system_message,
        genai_prompt=genai_prompt,
        tags=[TagRead(**tag.__dict__)],
        entity_types=[EntityTypeRead(**entity_type.__dict__)]
    )
    signal = create(db_session=session, signal_in=signal_in)
    assert signal


def test_update(session, project, signal, case_priority, case_type, service, tag, entity_type):
    from dispatch.signal.models import SignalUpdate, Service, TagRead, EntityTypeRead, ProjectRead, CasePriorityRead, CaseTypeRead
    from dispatch.signal.service import update

    name = "Updated name"
    owner = "example@test.com"
    external_id = "foo"
    external_url = "http://example.com"
    conversation_target = "#general"
    variant = "v1"
    lifecycle = "active"
    runbook = "http://runbook.com"
    genai_model = "gpt-4"
    genai_system_message = "system"
    genai_prompt = "prompt"

    signal_in = SignalUpdate(
        id=signal.id,
        name=name,
        owner=owner,
        project=ProjectRead(**project.__dict__),
        case_priority=CasePriorityRead(**case_priority.__dict__),
        case_type=CaseTypeRead(**case_type.__dict__),
        conversation_target=conversation_target,
        external_id=external_id,
        external_url=external_url,
        description="desc",
        oncall_service=Service(**service.__dict__),
        source=None,
        variant=variant,
        lifecycle=lifecycle,
        runbook=runbook,
        genai_model=genai_model,
        genai_system_message=genai_system_message,
        genai_prompt=genai_prompt,
        tags=[TagRead(**tag.__dict__)],
        entity_types=[EntityTypeRead(**entity_type.__dict__)]
    )
    signal = update(
        db_session=session,
        signal=signal,
        signal_in=signal_in,
    )
    assert signal.name == name


def test_update__add_filter(session, signal, signal_filter, project, case_priority, case_type, service, tag, entity_type):
    from dispatch.signal.models import SignalUpdate, SignalFilterRead, Service, TagRead, EntityTypeRead, ProjectRead, CasePriorityRead, CaseTypeRead
    from dispatch.signal.service import update

    signal_filter.project = signal.project

    signal_in = SignalUpdate(
        id=signal.id,
        name=signal.name,
        project=ProjectRead(**project.__dict__),
        owner="example.com",
        external_id="foo",
        case_priority=CasePriorityRead(**case_priority.__dict__),
        case_type=CaseTypeRead(**case_type.__dict__),
        conversation_target="#general",
        description="desc",
        external_url="http://example.com",
        oncall_service=Service(**service.__dict__),
        source=None,
        variant="v1",
        lifecycle="active",
        runbook="http://runbook.com",
        genai_model="gpt-4",
        genai_system_message="system",
        genai_prompt="prompt",
        tags=[TagRead(**tag.__dict__)],
        entity_types=[EntityTypeRead(**entity_type.__dict__)],
        filters=[SignalFilterRead.from_orm(signal_filter)],
    )
    signal = update(
        db_session=session,
        signal=signal,
        signal_in=signal_in,
    )
    assert hasattr(signal, "filters") and len(signal.filters) == 1


def test_update__delete_filter(session, signal, signal_filter, project, case_priority, case_type, service, tag, entity_type):
    from dispatch.signal.models import SignalUpdate, Service, TagRead, EntityTypeRead, ProjectRead, CasePriorityRead, CaseTypeRead
    from dispatch.signal.service import update

    # Set up conditions to delete a signal filter.
    signal_filter.project = signal.project
    signal.filters.append(signal_filter)

    assert hasattr(signal, "filters") and len(signal.filters) == 1

    signal_in = SignalUpdate(
        id=signal.id,
        name=signal.name,
        project=ProjectRead(**project.__dict__),
        owner="example.com",
        external_id="foo",
        case_priority=CasePriorityRead(**case_priority.__dict__),
        case_type=CaseTypeRead(**case_type.__dict__),
        conversation_target="#general",
        description="desc",
        external_url="http://example.com",
        oncall_service=Service(**service.__dict__),
        source=None,
        variant="v1",
        lifecycle="active",
        runbook="http://runbook.com",
        genai_model="gpt-4",
        genai_system_message="system",
        genai_prompt="prompt",
        tags=[TagRead(**tag.__dict__)],
        entity_types=[EntityTypeRead(**entity_type.__dict__)],
        filters=[],
    )
    signal = update(
        db_session=session,
        signal=signal,
        signal_in=signal_in,
    )
    assert hasattr(signal, "filters") and len(signal.filters) == 0


def test_delete(session, signal):
    from dispatch.signal.service import delete, get

    delete(db_session=session, signal_id=signal.id)
    assert not get(db_session=session, signal_id=signal.id)


def test_filter_actions_default_deduplicate(session, signal, project):
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, CaseFactory, SignalInstanceFactory
    from datetime import datetime, timedelta
    import json

    entity_type = EntityTypeFactory(project=project)
    session.add(entity_type)

    entity = EntityFactory(entity_type=entity_type, project=project)
    session.add(entity)

    # Create a case for the first signal instance
    case = CaseFactory(project=project)
    session.add(case)
    session.commit()

    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        case=case,
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)

    signal_instance_2 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_2)
    session.commit()

    assert filter_signal(db_session=session, signal_instance=signal_instance_2)
    assert signal_instance_2.filter_action == SignalFilterAction.deduplicate

    # Test default deduplication logic within the 1-hour window
    signal_instance_3 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
        created_at=datetime.now() - timedelta(minutes=30),
    )
    session.add(signal_instance_3)
    session.commit()

    assert filter_signal(db_session=session, signal_instance=signal_instance_3)
    assert signal_instance_3.filter_action == SignalFilterAction.deduplicate


def test_filter_actions_deduplicate_different_entities(session, signal, project):
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type_0 = EntityTypeFactory(project=project)
    session.add(entity_type_0)
    entity_0 = EntityFactory(entity_type=entity_type_0, project=project)
    session.add(entity_0)
    signal_instance_0 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity_0],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_0)

    entity_type_1 = EntityTypeFactory(project=project)
    session.add(entity_type_1)
    entity_1 = EntityFactory(entity_type=entity_type_1, project=project)
    session.add(entity_1)

    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity_1],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)
    session.commit()

    # create deduplicate signal filter
    signal_filter = SignalFilterFactory(
        name="test",
        description="dedupe0",
        expression=[{"or": [{"model": "EntityType", "field": "id", "op": "==", "value": entity_type_1.id}]}],
        action="deduplicate",
        window=5,
        project=project,
    )
    signal.filters.append(signal_filter)

    session.commit()
    assert not filter_signal(db_session=session, signal_instance=signal_instance_1)
    assert signal_instance_1.filter_action == SignalFilterAction.none


def test_filter_actions_deduplicate_different_entities_types(session, signal, project):
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type_0 = EntityTypeFactory(project=project)
    session.add(entity_type_0)
    entity_0 = EntityFactory(entity_type=entity_type_0, project=project)
    session.add(entity_0)
    signal_instance_0 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity_0],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_0)

    entity_type_1 = EntityTypeFactory(project=project)
    session.add(entity_type_1)
    entity_1 = EntityFactory(entity_type=entity_type_1, project=project)
    session.add(entity_1)

    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity_1],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)
    session.commit()

    # create deduplicate signal filter
    signal_filter = SignalFilterFactory(
        name="test",
        description="dedupe0",
        expression=[{"or": [{"model": "EntityType", "field": "id", "op": "==", "value": entity_type_1.id}]}],
        action="deduplicate",
        window=5,
        project=project,
    )
    signal.filters.append(signal_filter)

    session.commit()
    assert not filter_signal(db_session=session, signal_instance=signal_instance_1)
    assert signal_instance_1.filter_action == SignalFilterAction.none


def test_filter_actions_deduplicate(session, signal, project):
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type = EntityTypeFactory(project=project)
    session.add(entity_type)

    entity = EntityFactory(entity_type=entity_type, project=project)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)

    signal_instance_2 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_2)
    session.commit()
    # create deduplicate signal filter
    signal_filter = SignalFilterFactory(
        name="dedupe1",
        description="test",
        expression=[{"or": [{"model": "EntityType", "field": "id", "op": "==", "value": entity_type.id}]}],
        action="deduplicate",
        window=5,
        project=project,
    )
    signal.filters.append(signal_filter)

    session.commit()
    assert filter_signal(db_session=session, signal_instance=signal_instance_2)
    assert signal_instance_2.filter_action == SignalFilterAction.deduplicate


def test_filter_action_with_dedupe_and_snooze(session, signal, project):
    from datetime import datetime, timedelta, timezone
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type = EntityTypeFactory(project=project)
    session.add(entity_type)

    entity = EntityFactory(entity_type=entity_type, project=project)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)

    signal_instance_2 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_2)
    session.commit()
    # create deduplicate signal filter
    signal_filter = SignalFilterFactory(
        name="dedupe1",
        description="test",
        expression=[{"or": [{"model": "EntityType", "field": "id", "op": "==", "value": entity_type.id}]}],
        action="deduplicate",
        window=5,
        project=project,
    )
    signal.filters.append(signal_filter)

    signal_filter = SignalFilterFactory(
        name="snooze0",
        description="test",
        expression=[{"or": [{"model": "Entity", "field": "id", "op": "==", "value": entity.id}]}],
        action="snooze",
        expiration=datetime.now(tz=timezone.utc) + timedelta(minutes=5),
        project=project,
    )
    signal.filters.append(signal_filter)

    session.commit()
    assert filter_signal(db_session=session, signal_instance=signal_instance_2)
    assert signal_instance_2.filter_action == SignalFilterAction.snooze


def test_filter_actions_snooze(session, entity, signal, project):
    from datetime import datetime, timedelta, timezone
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type = EntityTypeFactory(project=project)
    session.add(entity_type)
    signal.entity_types.append(entity_type)

    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)
    session.commit()

    signal_filter = SignalFilterFactory(
        name="snooze0",
        description="test",
        expression=[{"or": [{"model": "Entity", "field": "id", "op": "==", "value": entity.id}]}],
        action="snooze",
        expiration=datetime.now(timezone.utc) + timedelta(minutes=5),
        project=project,
    )

    signal.filters = [signal_filter]

    session.commit()
    assert filter_signal(db_session=session, signal_instance=signal_instance_1)
    assert signal_instance_1.filter_action == SignalFilterAction.snooze


def test_filter_actions_snooze_expired(session, entity, signal, project):
    from datetime import datetime, timedelta, timezone
    from dispatch.signal.models import SignalFilterAction
    from dispatch.signal.service import filter_signal
    from tests.factories import EntityTypeFactory, EntityFactory, SignalInstanceFactory, SignalFilterFactory
    import json

    entity_type = EntityTypeFactory(project=project)
    session.add(entity_type)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstanceFactory(
        project=project,
        signal=signal,
        entities=[entity],
        raw=json.dumps({"id": "foo"}),
    )
    session.add(signal_instance_1)

    # expired
    signal_filter = SignalFilterFactory(
        name="snooze1",
        description="test",
        expression=[{"or": [{"model": "Entity", "field": "id", "op": "==", "value": 1}]}],
        action="snooze",
        expiration=datetime.now(timezone.utc) - timedelta(minutes=5),
        project=project,
    )

    signal.filters = [signal_filter]
    session.commit()
    assert not filter_signal(db_session=session, signal_instance=signal_instance_1)
