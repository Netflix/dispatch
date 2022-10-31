def test_get(session, incident_type):
    from dispatch.incident.type.service import get

    t_incident_type = get(db_session=session, incident_type_id=incident_type.id)
    assert t_incident_type.id == incident_type.id


def test_get_by_name(session, incident_type):
    from dispatch.incident.type.service import get_by_name

    t_incident_type = get_by_name(
        db_session=session, project_id=incident_type.project.id, name=incident_type.name
    )
    assert t_incident_type.name == incident_type.name


def test_get_by_slug(session, incident_type):
    from dispatch.incident.type.service import get_by_slug

    t_incident_type = get_by_slug(
        db_session=session, project_id=incident_type.project.id, slug=incident_type.slug
    )
    assert t_incident_type.slug == incident_type.slug


def test_get_all(session, project, incident_types):
    from dispatch.incident.type.service import get_all

    t_incident_types = get_all(db_session=session, project_id=incident_types[0].project.id).all()
    assert t_incident_types


def test_create(session, project, document):
    from dispatch.incident.type.service import create
    from dispatch.incident.type.models import IncidentTypeCreate

    name = "XXX"

    incident_type_in = IncidentTypeCreate(
        name=name,
        template_document=document,
        project=project,
    )

    incident_type = create(db_session=session, incident_type_in=incident_type_in)
    assert incident_type


def test_update(session, incident_type):
    from dispatch.incident.type.service import update
    from dispatch.incident.type.models import IncidentTypeUpdate

    name = "Updated incident type name"

    incident_type_in = IncidentTypeUpdate(name=name)
    incident_type = update(
        db_session=session,
        incident_type=incident_type,
        incident_type_in=incident_type_in,
    )
    assert incident_type.name == name


def test_delete(session, incident_type):
    from dispatch.incident.type.service import delete, get

    delete(db_session=session, incident_type_id=incident_type.id)
    assert not get(db_session=session, incident_type_id=incident_type.id)
