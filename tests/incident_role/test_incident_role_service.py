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


def test_create_update(session, incident_type, project_fixture):
    from dispatch.incident_role.service import create_or_update
    from dispatch.incident_role.models import IncidentRoleCreateUpdate
    from dispatch.participant_role.models import ParticipantRoleType
    from dispatch.project.models import ProjectRead
    from dispatch.incident.type.models import IncidentTypeRead

    # Ensure incident_type.project is the same as project_fixture if used interchangeably
    # For clarity, using project_fixture where ProjectRead is needed by service.
    project_read_in = ProjectRead.model_validate(project_fixture)

    # test create (no id)
    incident_role_in_create = IncidentRoleCreateUpdate(
        enabled=True,
        tags=[],
        order=1,
        incident_types=[],
        incident_priorities=[],
        service=None,
        individual=None,
        engage_next_oncall=False,
        project=project_read_in
    )
    created_roles = create_or_update(
        db_session=session,
        project_in=project_read_in,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[incident_role_in_create],
    )

    assert len(created_roles) == 1
    assert created_roles[0].role == ParticipantRoleType.incident_commander
    assert created_roles[0].project.id == project_fixture.id

    # test update (with id)
    incident_role_in_update = IncidentRoleCreateUpdate(
        id=created_roles[0].id,
        enabled=True,
        tags=[],
        order=2,
        incident_types=[IncidentTypeRead.model_validate(incident_type)],
        incident_priorities=[],
        service=None,
        individual=None,
        engage_next_oncall=True,
        project=project_read_in
    )
    updated_roles = create_or_update(
        db_session=session,
        project_in=project_read_in,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[incident_role_in_update],
    )
    assert len(updated_roles) == 1
    assert updated_roles[0].id == created_roles[0].id
    assert updated_roles[0].order == 2
    assert updated_roles[0].engage_next_oncall is True
    assert len(updated_roles[0].incident_types) == 1
    assert updated_roles[0].incident_types[0].id == incident_type.id

    # test removal
    removed_roles = create_or_update(
        db_session=session,
        project_in=project_read_in,
        role=ParticipantRoleType.incident_commander,
        incident_roles_in=[],
    )

    assert not removed_roles


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
