import pytest


def test_get_service(session, service):
    from dispatch.service.service import get

    t_service = get(db_session=session, service_id=service.id)
    assert t_service.id == service.id


def test_get_by_external_id(session, service):
    from dispatch.service.service import get_by_external_id

    t_service = get_by_external_id(db_session=session, external_id=service.external_id)
    assert t_service.external_id == service.external_id


def test_get_by_status(session, services):
    from dispatch.service.service import get_all_by_status

    t_services = get_all_by_status(db_session=session, is_active=True).all()
    assert len(t_services) > 1


def test_get_all(session, services):
    from dispatch.service.service import get_all

    t_services = get_all(db_session=session).all()

    assert len(t_services) > 1


def test_create(session):
    from dispatch.service.service import create
    from dispatch.service.models import ServiceCreate

    name = "createName"
    service_in = ServiceCreate(name=name)

    service = create(db_session=session, service_in=service_in)
    assert name == service.name


@pytest.mark.skip
def test_update(session, service):
    from dispatch.service.service import update
    from dispatch.service.models import ServiceUpdate

    name = "nameUpdate"
    service_in = ServiceUpdate(name=name)

    service = update(db_session=session, service=service, service_in=service_in)
    assert service.name == name


def test_delete(session, service):
    from dispatch.service.service import delete, get

    delete(db_session=session, service_id=service.id)
    assert not get(db_session=session, service_id=service.id)
