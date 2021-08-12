from tests.conftest import db


def test_get(session, incident_role):
    from dispatch.incident_role.service import get

    t_incident_role = get(db_session=session, incident_role_id=incident_role.id)
    assert t_incident_role.id == incident_role.id


def test_get_all(session, project, incident_roles):
    from dispatch.incident_role.service import get_all

    t_incident_roles = get_all(db_session=session, project_id=incident_roles[0].project.id).all()
    assert len(t_incident_roles) >= 1


def test_get_all_enabled(session, project, incident_roles):
    from dispatch.incident_role.service import get_all_enabled

    t_incident_roles = get_all_enabled(
        db_session=session, project_id=incident_roles[0].project.id
    ).all()
    assert len(t_incident_roles) >= 1


def test_create(session, project, incident_type, tag, incident_priority, service):
    from dispatch.incident_role.service import create
    from dispatch.participant_role.models import ParticipantRoleType
    from dispatch.incident_role.models import IncidentRoleCreate

    incident_role_in = IncidentRoleCreate(
        role=ParticipantRoleType.incident_commander,
        incident_types=[incident_type],
        tags=[tag],
        incident_priorities=[incident_priority],
        service=service,
        project=project,
    )

    incident_role = create(db_session=session, incident_role_in=incident_role_in)
    assert incident_role


def test_update(session, incident_role):
    from dispatch.incident_role.service import update
    from dispatch.incident_role.models import IncidentRoleUpdate
    from dispatch.participant_role.models import ParticipantRoleType

    incident_role_in = IncidentRoleUpdate(role=ParticipantRoleType.liaison)
    incident_role = update(
        db_session=session,
        incident_role=incident_role,
        incident_role_in=incident_role_in,
    )
    assert incident_role.role == ParticipantRoleType.liaison


def test_delete(session, incident_role):
    from dispatch.incident_role.service import delete, get

    delete(db_session=session, incident_role_id=incident_role.id)
    assert not get(db_session=session, incident_role_id=incident_role.id)


def test_resolve_role(session, project, incident, incident_type, tag, incident_priority, service):
    from dispatch.incident_role.service import create
    from dispatch.incident_role.service import resolve_role
    from dispatch.participant_role.models import ParticipantRoleType
    from dispatch.incident_role.models import IncidentRoleCreate

    incident_role_in = IncidentRoleCreate(
        role=ParticipantRoleType.incident_commander,
        incident_types=[incident_type],
        tags=[tag],
        incident_priorities=[incident_priority],
        service=service,
        project=project,
    )

    create(db_session=session, incident_role_in=incident_role_in)
    incident.incident_priority = incident_priority
    matching_role = resolve_role(
        db_session=session, role=ParticipantRoleType.incident_commander, incident=incident
    )

    assert matching_role
