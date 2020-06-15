import pytest


@pytest.mark.skip
def test_incident_create(session):
    from dispatch.incident.service import create
    from dispatch.incident.models import IncidentCreate

    incident_type = {}
    incident_priority = {}
    incident_priority["name"] = "Low"
    incident_type["name"] = "Simulation"
    reporter_email = "fmonsen@netflix.com"
    title = "Test"
    status = "Active"
    description = "Test test"
    tags = ["test"]

    # incident_in = IncidentCreate(incident_priority=incident_priority, incident_type=incident_type)

    incident = create(
        db_session=session,
        incident_priority=incident_priority,
        incident_type=incident_type,
        reporter_email=reporter_email,
        title=title,
        status=status,
        description=description,
        tags=tags,
    )

    assert incident


def test_incident_get(session, incident):
    from dispatch.incident.service import get

    test_incident = get(db_session=session, incident_id=incident.id)

    assert test_incident.id == incident.id
