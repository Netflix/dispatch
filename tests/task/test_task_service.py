import pytest


def test_get(session, task):
    from dispatch.task.service import get

    t_task = get(db_session=session, task_id=task.id)
    assert t_task.id == task.id


@pytest.mark.skip  # NOTE: refactor create function in the task service module before enabling this test
def test_create(
    session, incident, incident_type, incident_priority, participant, individual_contact
):
    from dispatch.task.service import create
    from dispatch.task.models import TaskCreate

    incident.incident_type = incident_type
    incident.incident_priority = incident_priority
    participant.individual = individual_contact

    task_in = TaskCreate(incident=incident, owner=participant)
    task = create(db_session=session, task_in=task_in)
    assert task


@pytest.mark.skip
def test_update(session, task):
    from dispatch.task.service import update
    from dispatch.task.models import TaskUpdate

    description = "Updated description"

    task_in = TaskUpdate(
        description=description,
    )
    task = update(
        db_session=session,
        task=task,
        task_in=task_in,
    )
    assert task.description == description


def test_delete(session, task):
    from dispatch.task.service import delete, get

    delete(db_session=session, task_id=task.id)
    assert not get(db_session=session, task_id=task.id)
