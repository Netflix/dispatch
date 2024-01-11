from dispatch.entity_type.models import EntityType
from dispatch.entity import service as entity_service
from tests.factories import SignalInstanceFactory


def test_get(session, entity):
    from dispatch.entity.service import get

    t_entity = get(db_session=session, entity_id=entity.id)
    assert t_entity.id == entity.id


def test_get_all_by_signal(session, entity, signal_instance):
    from dispatch.entity.service import get_all_by_signal

    # Associate the entity with the signal_instance
    signal_instance.entities.append(entity)
    session.add(signal_instance)
    session.commit()

    # Get the signal_id for the test
    signal_id = signal_instance.signal_id

    # Call the function to get all entities by signal
    entities = get_all_by_signal(db_session=session, signal_id=signal_id)

    # Check if the entity is in the list of entities returned by the function
    assert entity in entities

    # Check that the number of entities returned is correct
    assert len(entities) == 1

    # Check that the entity returned is the one appended to the signal instance
    assert entities[0].id == entity.id


def test_create(session, entity_type, project):
    from dispatch.entity.models import EntityCreate
    from dispatch.entity.service import create

    name = "name"
    description = "description"

    entity_in = EntityCreate(
        name=name,
        owner="example@test.com",
        external_id="foo",
        description=description,
        entity_type=entity_type,
        project=project,
    )
    entity = create(db_session=session, entity_in=entity_in)
    assert entity


def test_update(session, project, entity):
    from dispatch.entity.models import EntityUpdate
    from dispatch.entity.service import update

    name = "Updated name"

    entity_in = EntityUpdate(
        id=entity.id, name=name, project=project, owner="example.com", external_id="foo"
    )
    entity = update(
        db_session=session,
        entity=entity,
        entity_in=entity_in,
    )
    assert entity.name == name


def test_delete(session, entity):
    from dispatch.entity.service import delete, get

    entity_id = entity.id

    delete(db_session=session, entity_id=entity_id)
    assert not get(db_session=session, entity_id=entity_id)


def test_find_entities_with_field_only(session, signal_instance, project):
    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            jpath="id",
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 1

    # An entire obj which is not valid
    entity_types = [
        EntityType(
            name="Entire Obj",
            jpath="identity",
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 0

    # Two matches
    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            jpath="asset[*].id",
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 2


def test_find_entities_with_no_regex_or_field(session, signal_instance, project):
    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            jpath=None,
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 0


def test_find_entities_handles_key_error(session, signal_instance, project):
    # Define an entity type that will cause a KeyError due to incorrect JSONPath usage
    # The JSONPath expression tries to access a dictionary with an index, which is invalid
    entity_type_with_invalid_jsonpath = EntityType(
        name="EntityType with Invalid JSONPath",
        jpath="dictionary[0].value",
        regular_expression=None,
        project=project,
    )

    # Override the signal_instance fixture to include problematic 'dictionary' field
    # that is a dictionary, not a list
    signal_instance = SignalInstanceFactory(
        raw={
            "id": "4893bde0-f8bc-4472-a7dc-8b44b26b2198",
            "dictionary": {
                "value": "pompompurin",
            },
        }
    )

    # Attempt to find entities using the entity type with the invalid JSONPath expression
    entities = entity_service.find_entities(
        session, signal_instance, [entity_type_with_invalid_jsonpath]
    )

    # The service should handle the KeyError and not return any entities for the invalid JSONPath
    assert len(entities) == 0


def test_find_entities_multiple_entity_types(session, signal_instance, project):
    # A test that checks if the function correctly processes multiple entity types, some valid and some invalid.
    entity_type_valid = EntityType(
        name="EntityType with Valid JSONPath and Regex",
        jpath="dictionary.value",
        regular_expression=None,
        project=project,
    )

    entity_type_invalid_jsonpath = EntityType(
        name="EntityType with Invalid JSONPath",
        jpath="dictionary[0].value",
        regular_expression=None,
        project=project,
    )

    signal_instance = SignalInstanceFactory(
        raw={
            "id": "4893bde0-f8bc-4472-a7dc-8b44b26b2198",
            "dictionary": {
                "value": "pompompurin",
            },
        }
    )

    entities = entity_service.find_entities(
        session, signal_instance, [entity_type_valid, entity_type_invalid_jsonpath]
    )

    # The service should find one entity with valid JSONPath and Regex and ignore the invalid one
    assert len(entities) == 1
    assert entities[0].value == "pompompurin"
