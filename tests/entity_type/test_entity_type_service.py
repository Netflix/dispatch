def test_get(session, entity_type):
    from dispatch.entity_type.service import get

    t_entity_type = get(db_session=session, entity_type_id=entity_type.id)
    assert t_entity_type is not None and hasattr(t_entity_type, 'id') and t_entity_type.id == entity_type.id


def test_create(session, project):
    from dispatch.entity_type.models import EntityTypeCreate
    from dispatch.entity_type.service import create
    from dispatch.project.models import ProjectRead
    from dispatch.entity_type.models import EntityScopeEnum

    name = "name"
    description = "description"

    entity_type_in = EntityTypeCreate(
        id=None,
        name=name,
        description=description,
        jpath="foo",
        regular_expression="*.",
        enabled=False,
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
    )
    entity_type = create(db_session=session, entity_type_in=entity_type_in)
    assert entity_type


def test_update(session, project, entity_type):
    from dispatch.entity_type.models import EntityTypeUpdate
    from dispatch.entity_type.service import update
    from dispatch.entity_type.models import EntityScopeEnum

    name = "Updated name"

    entity_type_in = EntityTypeUpdate(
        id=entity_type.id,
        name=name,
        description=entity_type.description,
        jpath=entity_type.jpath,
        regular_expression=entity_type.regular_expression,
        enabled=entity_type.enabled,
        scope=EntityScopeEnum.single,
        signals=[],
    )
    entity_type = update(
        db_session=session,
        entity_type=entity_type,
        entity_type_in=entity_type_in,
    )
    assert entity_type is not None and getattr(entity_type, 'name', None) == name


def test_delete(session, entity_type):
    from dispatch.entity_type.service import delete, get

    delete(db_session=session, entity_type_id=entity_type.id)
    assert not get(db_session=session, entity_type_id=entity_type.id)


def test_set_jpath(entity_type):
    from dispatch.entity_type.service import set_jpath
    from dispatch.entity_type.models import EntityTypeCreate

    entity_type_in = EntityTypeCreate.from_orm(entity_type)
    entity_type_in.jpath = "$.foo.bar[0].foobar"

    set_jpath(entity_type, entity_type_in)
    assert entity_type.jpath == "$.foo.bar[0].foobar"


def test_set_jpath__fail(entity_type):
    from dispatch.entity_type.service import set_jpath
    from dispatch.entity_type.models import EntityTypeCreate

    entity_type_in = EntityTypeCreate.from_orm(entity_type)
    entity_type_in.jpath = "?"

    set_jpath(entity_type, entity_type_in)
    assert entity_type.jpath == ""
