def test_get(session, incident_priority):
    from dispatch.incident.priority.service import get

    t_incident_priority = get(db_session=session, incident_priority_id=incident_priority.id)
    assert t_incident_priority.id == incident_priority.id


def test_get_by_name(session, incident_priority):
    from dispatch.incident.priority.service import get_by_name

    t_incident_priority = get_by_name(
        db_session=session, project_id=incident_priority.project.id, name=incident_priority.name
    )
    assert t_incident_priority.name == incident_priority.name


def test_get_all(session, project, incident_priorities):
    from dispatch.incident.priority.service import get_all

    t_incident_priorities = get_all(
        db_session=session, project_id=incident_priorities[0].project.id
    ).all()
    assert t_incident_priorities


def test_create(session, project):
    from dispatch.incident.priority.service import create
    from dispatch.incident.priority.models import IncidentPriorityCreate

    name = "XXX"
    description = "XXXXXX"

    incident_priority_in = IncidentPriorityCreate(
        name=name,
        description=description,
        project=project,
    )
    incident_priority = create(db_session=session, incident_priority_in=incident_priority_in)
    assert incident_priority


def test_update(session, incident_priority):
    from dispatch.incident.priority.service import update
    from dispatch.incident.priority.models import IncidentPriorityUpdate

    name = "Updated incident priority name"

    incident_priority_in = IncidentPriorityUpdate(name=name)
    incident_priority = update(
        db_session=session,
        incident_priority=incident_priority,
        incident_priority_in=incident_priority_in,
    )
    assert incident_priority.name == name


def test_delete(session, incident_priority):
    from dispatch.incident.priority.service import delete, get

    delete(db_session=session, incident_priority_id=incident_priority.id)
    assert not get(db_session=session, incident_priority_id=incident_priority.id)
