def test_get(session, entity_type):
    from dispatch.entity_type.service import get

    t_entity_type = get(db_session=session, entity_type_id=entity_type.id)
    assert t_entity_type.id == entity_type.id


def test_create(session, project):
    from dispatch.entity_type.models import EntityTypeCreate
    from dispatch.entity_type.service import create

    name = "name"
    description = "description"

    entity_type_in = EntityTypeCreate(
        name=name,
        description=description,
        jpath="foo",
        regular_expression="*.",
        enabled=False,
        project=project,
    )
    entity_type = create(db_session=session, entity_type_in=entity_type_in)
    assert entity_type


def test_update(session, project, entity_type):
    from dispatch.entity_type.models import EntityTypeUpdate
    from dispatch.entity_type.service import update

    name = "Updated name"

    entity_type_in = EntityTypeUpdate(
        id=entity_type.id,
        name=name,
        project=project,
    )
    entity_type = update(
        db_session=session,
        entity_type=entity_type,
        entity_type_in=entity_type_in,
    )
    assert entity_type.name == name


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
