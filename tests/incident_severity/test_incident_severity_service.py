def test_get(session, incident_severity):
    from dispatch.incident.severity.service import get

    t_incident_severity = get(db_session=session, incident_severity_id=incident_severity.id)
    assert t_incident_severity.id == incident_severity.id


def test_get_default(session, incident_severity):
    from dispatch.incident.severity.service import get_default

    incident_severity.default = True

    t_incident_severity = get_default(db_session=session, project_id=incident_severity.project.id)
    assert t_incident_severity.id == incident_severity.id


def test_get_default_or_raise__fail(session, incident_severity):
    from pydantic_core import PydanticCustomError
    from pydantic import ValidationError
    from dispatch.incident.severity.service import get_default_or_raise

    incident_severity.default = False
    validation_error = False

    try:
        get_default_or_raise(db_session=session, project_id=incident_severity.project.id)
    except ValidationError:
        validation_error = True

    assert validation_error


def test_get_by_name(session, incident_severity):
    from dispatch.incident.severity.service import get_by_name

    assert get_by_name(
        db_session=session, project_id=incident_severity.project_id, name=incident_severity.name
    )


def get_by_name_or_raise__fail(session, incident_severity):
    """Returns the incident severity specified or raises ValidationError."""
    from pydantic_core import PydanticCustomError
    from pydantic import ValidationError
    from dispatch.incident.severity.models import IncidentSeverityRead
    from dispatch.incident.severity.service import get_by_name_or_raise

    incident_severity_in = IncidentSeverityRead.from_orm(incident_severity)
    incident_severity_in.name += "_fail"
    validation_error = False

    try:
        get_by_name_or_raise(
            db_session=session,
            project_id=incident_severity.project.id,
            incident_severity_in=incident_severity_in,
        )
    except ValidationError:
        validation_error = True

    assert validation_error


def test_get_by_name_or_default__name(session, incident_severity):
    from dispatch.incident.severity.models import IncidentSeverityRead
    from dispatch.incident.severity.service import get_by_name_or_default

    incident_severity_in = IncidentSeverityRead.from_orm(incident_severity)

    assert get_by_name_or_default(
        db_session=session,
        project_id=incident_severity.project_id,
        incident_severity_in=incident_severity_in,
    )


def test_get_by_name_or_default__default(session, incident_severity):
    from dispatch.incident.severity.service import get_by_name_or_default

    incident_severity.default = True

    assert get_by_name_or_default(
        db_session=session,
        project_id=incident_severity.project_id,
        incident_severity_in=None,
    )


def test_get_all(session, incident_severity):
    from dispatch.incident.severity.service import get_all

    assert get_all(
        db_session=session,
        project_id=incident_severity.project_id,
    )


def test_get_all_enabled(session, incident_severity):
    from dispatch.incident.severity.service import get_all_enabled

    incident_severity.enabled = True

    assert get_all_enabled(db_session=session, project_id=incident_severity.project_id)


def test_get_all_enabled__empty(session, incident_severity):
    from dispatch.incident.severity.service import get_all, get_all_enabled

    for severity in get_all(
        db_session=session,
        project_id=incident_severity.project_id,
    ):
        severity.enabled = False

    assert not get_all_enabled(db_session=session, project_id=incident_severity.project_id).all()


def test_create(session, incident_severity):
    from dispatch.project.models import ProjectRead
    from dispatch.incident.severity.models import IncidentSeverityCreate
    from dispatch.incident.severity.service import create

    incident_severity_in = IncidentSeverityCreate(
        name="new_name",
        description="new_description",
        color="FFFFFF",
        project=ProjectRead.from_orm(incident_severity.project),
    )

    assert create(db_session=session, incident_severity_in=incident_severity_in)


def test_update(session, incident_severity):
    from dispatch.incident.severity.models import IncidentSeverityUpdate
    from dispatch.incident.severity.service import update

    expected_name = incident_severity.name + "_updated"
    incident_severity_in = IncidentSeverityUpdate.from_orm(incident_severity)
    incident_severity_in.name = expected_name
    incident_severity_in.enabled = True
    incident_severity_in.default = False

    t_incident_severity = update(
        db_session=session,
        incident_severity=incident_severity,
        incident_severity_in=incident_severity_in,
    )

    assert t_incident_severity.name == expected_name


def test_delete(session, incident_severity):
    from dispatch.incident.severity.service import get, delete

    delete(db_session=session, incident_severity_id=incident_severity.id)
    assert not get(db_session=session, incident_severity_id=incident_severity.id)
