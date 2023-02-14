from dispatch.entity_type.models import EntityType
from dispatch.entity import service as entity_service


def test_find_entities_with_field_and_regex(session, signal_instance, project):
    signal_instance = _setup_project(
        session=session, signal_instance=signal_instance, project=project
    )

    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            field="id",
            regular_expression=r"^arn:aws:iam::\d{12}:role\/[a-zA-Z_0-9+=,.@\-_/]+$",
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 1


def test_find_entities_with_regex_only(session, signal_instance, project):
    signal_instance = _setup_project(
        session=session, signal_instance=signal_instance, project=project
    )

    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            field=None,
            regular_expression=r"^arn:aws:iam::\d{12}:role\/[a-zA-Z_0-9+=,.@\-_/]+$",
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 1


def test_find_entities_with_field_only(session, signal_instance, project):
    signal_instance = _setup_project(
        session=session, signal_instance=signal_instance, project=project
    )

    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            field="id",
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 3


def test_find_entities_with_no_regex_or_field(session, signal_instance, project):
    signal_instance = _setup_project(
        session=session, signal_instance=signal_instance, project=project
    )
    entity_types = [
        EntityType(
            name="AWS IAM Role ARN",
            field=None,
            regular_expression=None,
            project=project,
        ),
    ]
    entities = entity_service.find_entities(session, signal_instance, entity_types)
    assert len(entities) == 0


def _setup_project(session, signal_instance, project):
    signal_instance.project = project
    session.add(signal_instance)
    session.commit()
    return signal_instance
