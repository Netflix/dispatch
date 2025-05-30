def test_get(session, project):
    from dispatch.project.service import get

    t_project = get(db_session=session, project_id=project.id)
    assert t_project.id == project.id


def test_create(session, organization):
    from dispatch.project.service import create
    from dispatch.project.models import ProjectCreate
    from dispatch.organization.models import OrganizationRead
    import random

    name = "name"
    description = "description"
    default = True
    color = "red"

    # Convert organization to OrganizationRead
    org_read = OrganizationRead(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        description=organization.description,
    )

    # Generate a random integer ID for the project to avoid collisions
    # Use a high range to avoid conflicts with existing IDs
    project_id = random.randint(100000, 999999)

    project_in = ProjectCreate(
        id=project_id,
        name=name,
        description=description,
        default=default,
        color=color,
        organization=org_read,
        annual_employee_cost=50000,
        business_year_hours=2080,
        display_name="",
        owner_email=None,
        owner_conversation=None,
        send_daily_reports=True,
        send_weekly_reports=False,
        weekly_report_notification_id=None,
        enabled=True,
        storage_folder_one=None,
        storage_folder_two=None,
        storage_use_folder_one_as_primary=True,
        storage_use_title=False,
        allow_self_join=True,
        select_commander_visibility=True,
        report_incident_instructions=None,
        report_incident_title_hint=None,
        report_incident_description_hint=None,
        snooze_extension_oncall_service=None,
    )
    project = create(db_session=session, project_in=project_in)
    assert project


def test_update(session, project):
    from dispatch.project.service import update
    from dispatch.project.models import ProjectUpdate

    name = "Updated name"

    project_in = ProjectUpdate(
        id=project.id,
        name=name,
        annual_employee_cost=50000,
        business_year_hours=2080,
        snooze_extension_oncall_service=None,
        stable_priority_id=None,
        snooze_extension_oncall_service_id=None,
    )
    project = update(
        db_session=session,
        project=project,
        project_in=project_in,
    )
    assert project.name == name


def test_delete(session, project):
    from dispatch.project.service import delete, get

    delete(db_session=session, project_id=project.id)
    assert not get(db_session=session, project_id=project.id)


def test_get_by_name_or_default__name(session, project):
    from dispatch.project.models import ProjectRead
    from dispatch.project.service import get_by_name_or_default

    project_in = ProjectRead.from_orm(project)
    result = get_by_name_or_default(db_session=session, project_in=project_in)
    assert result.id == project.id


def test_get_by_name_or_default__default(session, project, organization):
    from dispatch.project.models import ProjectRead
    from dispatch.project.service import get_by_name_or_default

    # Ensure only one default project
    for p in session.query(type(project)).all():
        p.default = False
    project.default = True
    session.commit()
    # Pass a ProjectRead with a non-existent name
    project_in = ProjectRead(name="nonexistent", organization=organization)
    result = get_by_name_or_default(db_session=session, project_in=project_in)
    assert result.id == project.id
