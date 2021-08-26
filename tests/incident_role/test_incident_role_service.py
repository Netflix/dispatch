def test_get(session, incident_role):
    from dispatch.incident_role.service import get

    t_incident_role = get(db_session=session, incident_role_id=incident_role.id)
    assert t_incident_role.id == incident_role.id


def test_get_all(session, project, incident_role):
    from dispatch.incident_role.service import get_all

    t_incident_roles = get_all(db_session=session).all()
    assert len(t_incident_roles) >= 1


def test_get_all_by_role(session, project, incident_role):
    from dispatch.incident_role.service import get_all_by_role

    t_incident_roles = get_all_by_role(
        db_session=session, project_id=incident_role.project.id, role=incident_role.role
    )

    assert len(t_incident_roles) >= 1


def test_create_update(session, incident_type):
    from dispatch.incident_role.service import create_or_update
    from dispatch.incident_role.models import IncidentRoleCreateUpdate
    from dispatch.participant_role.models import ParticipantRoleType

    # test create (no id)
    incident_role_in = IncidentRoleCreateUpdate()
    incident_roles = create_or_update(
        db_session=session,
        project_in=incident_type.project,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[incident_role_in],
    )

    assert incident_roles[0].role == ParticipantRoleType.incident_commander

    # test update (with id)
    incident_role_in = IncidentRoleCreateUpdate(
        id=incident_roles[0].id, incident_types=[incident_type]
    )
    incident_roles = create_or_update(
        db_session=session,
        project_in=incident_type.project,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[incident_role_in],
    )

    assert incident_roles[0].incident_types

    # test removal
    incident_roles = create_or_update(
        db_session=session,
        project_in=incident_type.project,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[],
    )

    assert not incident_roles


def test_resolve_role(session, incident):
    from dispatch.incident_role.service import resolve_role
    from dispatch.incident_role.models import IncidentRole
    from dispatch.participant_role.models import ParticipantRoleType

    incident_role = IncidentRole(
        role=ParticipantRoleType.incident_commander,
        project=incident.project,
        incident_priorities=[incident.incident_priority],
        incident_types=[incident.incident_type],
    )
    session.add(incident_role)
    session.commit()

    matching_role = resolve_role(
        db_session=session, role=ParticipantRoleType.incident_commander, incident=incident
    )

    assert matching_role
