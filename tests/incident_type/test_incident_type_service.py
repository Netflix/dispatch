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


def test_update_cost_model(session, incident, incident_type, cost_model, incident_cost_type):
    """Updating the cost model field should immediately update the incident cost of all incidents with this incident type."""
    from dispatch.incident.models import IncidentStatus
    from dispatch.incident.type.service import update
    from dispatch.incident_cost import service as incident_cost_service
    from dispatch.incident_cost_type import service as incident_cost_type_service
    from dispatch.incident.type.models import IncidentTypeUpdate
    import datetime

    name = "Updated incident type name"

    incident_type_in = IncidentTypeUpdate(name=name)
    current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    # Initial setup.
    incident.status = IncidentStatus.active
    incident.incident_type = incident_type
    incident.project = incident_type.project

    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False

    incident_cost_type.project = incident_type.project
    incident_cost_type.default = True

    cost_model.project = incident_type.project
    incident_type_in.cost_model = cost_model

    incident_type = update(
        db_session=session,
        incident_type=incident_type,
        incident_type_in=incident_type_in,
    )
    assert incident_type.name == name

    # Assert that the incident cost was updated
    incident_cost = incident_cost_service.get_default_incident_response_cost(
        db_session=session, incident=incident
    )
    assert incident_cost
    assert incident_cost.updated_at > current_time


def test_delete(session, incident_type):
    from dispatch.incident.type.service import delete, get

    delete(db_session=session, incident_type_id=incident_type.id)
    assert not get(db_session=session, incident_type_id=incident_type.id)
