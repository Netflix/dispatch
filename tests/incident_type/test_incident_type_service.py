import pytest


def test_get(session, incident_type):
    from dispatch.incident_type.service import get

    t_incident_type = get(db_session=session, incident_type_id=incident_type.id)
    assert t_incident_type.id == incident_type.id


def test_get_by_name(session, incident_type):
    from dispatch.incident_type.service import get_by_name

    t_incident_type = get_by_name(db_session=session, name=incident_type.name)
    assert t_incident_type.name == incident_type.name


def test_get_by_slug(session, incident_type):
    from dispatch.incident_type.service import get_by_slug

    t_incident_type = get_by_slug(db_session=session, slug=incident_type.slug)
    assert t_incident_type.slug == incident_type.slug


def test_get_all(session, incident_types):
    from dispatch.incident_type.service import get_all

    t_incident_types = get_all(db_session=session).all()
    assert len(t_incident_types) > 1


def test_create(session, document):
    from dispatch.incident_type.service import create
    from dispatch.incident_type.models import IncidentTypeCreate

    name = "XXX"

    incident_type_in = IncidentTypeCreate(name=name, template_document=document)

    incident_type = create(db_session=session, incident_type_in=incident_type_in)
    assert incident_type


def test_delete(session, incident_type):
    from dispatch.incident_type.service import delete, get

    delete(db_session=session, incident_type_id=incident_type.id)
    assert not get(db_session=session, incident_type_id=incident_type.id)
