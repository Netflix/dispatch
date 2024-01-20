def test_get(session, incident_cost_type):
    from dispatch.incident_cost_type.service import get

    t_incident_cost_type = get(db_session=session, incident_cost_type_id=incident_cost_type.id)
    assert t_incident_cost_type.id == incident_cost_type.id


def test_get_all(session, incident_cost_types):
    from dispatch.incident_cost_type.service import get_all

    t_incident_cost_types = get_all(db_session=session)
    assert t_incident_cost_types


def test_create(session, project):
    from dispatch.incident_cost_type.service import create
    from dispatch.incident_cost_type.models import IncidentCostTypeCreate

    name = "name"
    description = "description"
    category = "category"
    details = {}
    default = True
    editable = False

    incident_cost_type_in = IncidentCostTypeCreate(
        name=name,
        description=description,
        category=category,
        details=details,
        default=default,
        editable=editable,
        project=project,
    )
    incident_cost_type = create(db_session=session, incident_cost_type_in=incident_cost_type_in)
    assert incident_cost_type


def test_update(session, incident_cost_type):
    from dispatch.incident_cost_type.service import update
    from dispatch.incident_cost_type.models import IncidentCostTypeUpdate

    name = "Updated name"

    incident_cost_type_in = IncidentCostTypeUpdate(
        name=name,
    )
    incident_cost_type = update(
        db_session=session,
        incident_cost_type=incident_cost_type,
        incident_cost_type_in=incident_cost_type_in,
    )
    assert incident_cost_type.name == name


def test_delete(session, incident_cost_type):
    from dispatch.incident_cost_type.service import delete, get

    delete(db_session=session, incident_cost_type_id=incident_cost_type.id)
    assert not get(db_session=session, incident_cost_type_id=incident_cost_type.id)
