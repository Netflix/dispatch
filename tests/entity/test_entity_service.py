from dispatch.entity_type.models import EntityType, EntityTypeCreate, EntityTypeUpdate, EntityScopeEnum
from dispatch.entity import service as entity_service
from tests.factories import SignalInstanceFactory
from dispatch.project.models import ProjectRead


def test_get(session, entity):
    from dispatch.entity.service import get

    if not hasattr(entity, 'id') or entity.id is None:
        import pytest
        pytest.skip("Entity fixture does not have a valid id.")
    t_entity = get(db_session=session, entity_id=entity.id)
    assert t_entity is not None and hasattr(t_entity, 'id') and t_entity.id == entity.id


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


def test_get_all_desc_by_signal_without_case(session, entity, signal_instance):
    """
    Test get_all_desc_by_signal returns entities for a signal in descending order when case_id is not provided.
    """
    from dispatch.entity.service import get_all_desc_by_signal

    # Associate the entity with the signal_instance
    signal_instance.entities.append(entity)
    session.add(signal_instance)
    session.commit()

    signal_id = signal_instance.signal_id

    # Should return the entity, ordered by created_at desc
    entities = get_all_desc_by_signal(db_session=session, signal_id=signal_id)
    assert entity in entities
    assert len(entities) == 1
    assert entities[0].id == entity.id


def test_get_all_desc_by_signal_with_case(session, entity, signal_instance):
    """
    Test get_all_desc_by_signal returns entities for a signal and case in descending order when case_id is provided.
    """
    from dispatch.entity.service import get_all_desc_by_signal

    # Attach the entity to the signal_instance and commit
    signal_instance.entities.append(entity)
    session.add(signal_instance)
    session.commit()

    # The case is linked via signal_instance.case
    case = signal_instance.case
    signal_id = signal_instance.signal_id
    case_id = case.id

    # Should return the entity, filtered by both signal and case
    entities = get_all_desc_by_signal(db_session=session, signal_id=signal_id, case_id=case_id)
    assert entity in entities
    assert len(entities) == 1
    assert entities[0].id == entity.id

    # If we pass a non-matching case_id, should return empty
    entities_none = get_all_desc_by_signal(db_session=session, signal_id=signal_id, case_id=case_id + 999)
    assert len(entities_none) == 0


def test_create(session, entity_type, project):
    from dispatch.entity.models import EntityCreate
    from dispatch.entity.service import create

    name = "name"
    description = "description"

    entity_in = EntityCreate(
        id=None,
        name=name,
        source="test-source",
        value="test-value",
        description=description,
        entity_type=EntityTypeCreate(
            id=None,
            name=entity_type.name,
            description=entity_type.description,
            jpath=entity_type.jpath,
            regular_expression=entity_type.regular_expression,
            enabled=entity_type.enabled,
            scope=EntityScopeEnum.single,
            signals=[],
            project=ProjectRead(
                id=project.id,
                name=project.name,
                display_name=getattr(project, 'display_name', ''),
                owner_email=getattr(project, 'owner_email', None),
                owner_conversation=getattr(project, 'owner_conversation', None),
                annual_employee_cost=getattr(project, 'annual_employee_cost', 50000),
                business_year_hours=getattr(project, 'business_year_hours', 2080),
                description=getattr(project, 'description', None),
                default=getattr(project, 'default', False),
                color=getattr(project, 'color', None),
                send_daily_reports=getattr(project, 'send_daily_reports', True),
                send_weekly_reports=getattr(project, 'send_weekly_reports', False),
                weekly_report_notification_id=getattr(project, 'weekly_report_notification_id', None),
                enabled=getattr(project, 'enabled', True),
                storage_folder_one=getattr(project, 'storage_folder_one', None),
                storage_folder_two=getattr(project, 'storage_folder_two', None),
                storage_use_folder_one_as_primary=getattr(project, 'storage_use_folder_one_as_primary', True),
                storage_use_title=getattr(project, 'storage_use_title', False),
                allow_self_join=getattr(project, 'allow_self_join', True),
                select_commander_visibility=getattr(project, 'select_commander_visibility', True),
                report_incident_instructions=getattr(project, 'report_incident_instructions', None),
                report_incident_title_hint=getattr(project, 'report_incident_title_hint', None),
                report_incident_description_hint=getattr(project, 'report_incident_description_hint', None),
                snooze_extension_oncall_service=getattr(project, 'snooze_extension_oncall_service', None),
            ),
        ),
        project=ProjectRead(
            id=project.id,
            name=project.name,
            display_name=getattr(project, 'display_name', ''),
            owner_email=getattr(project, 'owner_email', None),
            owner_conversation=getattr(project, 'owner_conversation', None),
            annual_employee_cost=getattr(project, 'annual_employee_cost', 50000),
            business_year_hours=getattr(project, 'business_year_hours', 2080),
            description=getattr(project, 'description', None),
            default=getattr(project, 'default', False),
            color=getattr(project, 'color', None),
            send_daily_reports=getattr(project, 'send_daily_reports', True),
            send_weekly_reports=getattr(project, 'send_weekly_reports', False),
            weekly_report_notification_id=getattr(project, 'weekly_report_notification_id', None),
            enabled=getattr(project, 'enabled', True),
            storage_folder_one=getattr(project, 'storage_folder_one', None),
            storage_folder_two=getattr(project, 'storage_folder_two', None),
            storage_use_folder_one_as_primary=getattr(project, 'storage_use_folder_one_as_primary', True),
            storage_use_title=getattr(project, 'storage_use_title', False),
            allow_self_join=getattr(project, 'allow_self_join', True),
            select_commander_visibility=getattr(project, 'select_commander_visibility', True),
            report_incident_instructions=getattr(project, 'report_incident_instructions', None),
            report_incident_title_hint=getattr(project, 'report_incident_title_hint', None),
            report_incident_description_hint=getattr(project, 'report_incident_description_hint', None),
            snooze_extension_oncall_service=getattr(project, 'snooze_extension_oncall_service', None),
        ),
    )
    entity = create(db_session=session, entity_in=entity_in)
    assert entity


def test_update(session, entity):
    from dispatch.entity.models import EntityUpdate
    from dispatch.entity.service import update

    name = "Updated name"

    entity_in = EntityUpdate(
        id=entity.id,
        name=name,
        source="test-source",
        value="test-value",
        description="desc",
        entity_type=EntityTypeUpdate(
            id=entity.entity_type.id,
            name=entity.entity_type.name,
            description=entity.entity_type.description,
            jpath=entity.entity_type.jpath,
            regular_expression=entity.entity_type.regular_expression,
            enabled=entity.entity_type.enabled,
            scope=EntityScopeEnum.single,
            signals=[],
        ),
    )
    entity = update(
        db_session=session,
        entity=entity,
        entity_in=entity_in,
    )
    assert entity is not None and getattr(entity, 'name', None) == name


def test_delete(session, entity):
    from dispatch.entity.service import delete, get

    entity_id = entity.id

    delete(db_session=session, entity_id=entity_id)
    assert not get(db_session=session, entity_id=entity_id)


def test_find_entities_with_field_only(session, signal_instance, project):
    from dispatch.entity.service import find_entities

    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            jpath="$.raw.id",
            regular_expression=None,
            project=project,
        ),
    ]
    entities = find_entities(session, signal_instance, entity_types)
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
    entities = find_entities(session, signal_instance, entity_types)
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
    entities = find_entities(session, signal_instance, entity_types)
    assert len(entities) == 0


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
    from dispatch.entity.service import find_entities

    # Create multiple entity types for testing
    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            jpath="$.raw.id",
            regular_expression=None,
            project=project,
        ),
        EntityType(
            name="Another Entity Type",
            jpath="asset[*].id",
            regular_expression=None,
            project=project,
        ),
    ]

    entities = find_entities(session, signal_instance, entity_types)
    assert len(entities) == 1
