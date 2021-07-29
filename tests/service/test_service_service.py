def test_get(session, service):
    from dispatch.service.service import get

    t_service = get(db_session=session, service_id=service.id)
    assert t_service.id == service.id


def test_create(session, project):
    from dispatch.service.service import create
    from dispatch.service.models import ServiceCreate

    name = "createName"
    service_in = ServiceCreate(
        name=name,
        project=project,
    )

    service = create(db_session=session, service_in=service_in)
    assert name == service.name


def test_update(session, service):
    from dispatch.service.service import update
    from dispatch.service.models import ServiceUpdate

    name = "Updated Name"
    service_in = ServiceUpdate(name=name)

    service = update(db_session=session, service=service, service_in=service_in)
    assert service.name == name


def test_delete(session, service):
    from dispatch.service.service import delete, get

    delete(db_session=session, service_id=service.id)
    assert not get(db_session=session, service_id=service.id)
