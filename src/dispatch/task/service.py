from datetime import datetime, timedelta
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_

from .models import Task, TaskStatus, TaskUpdate


def get(*, db_session, task_id: int) -> Optional[Task]:
    """Get a single task by ID."""
    return db_session.query(Task).filter(Task.id == task_id).first()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Task]:
    """Get a single task by resource id."""
    return db_session.query(Task).filter(Task.resource_id == resource_id).first()


def get_all(*, db_session) -> List[Optional[Task]]:
    """Return all tasks."""
    return db_session.query(Task)


def get_all_by_incident_id(*, db_session, incident_id: int) -> List[Optional[Task]]:
    """Get all tasks by incident id."""
    return db_session.query(Task).filter(Task.incident_id == incident_id)


def get_all_by_incident_id_and_status(
    *, db_session, incident_id: int, status: str
) -> List[Optional[Task]]:
    """Get all tasks by incident id and status."""
    return (
        db_session.query(Task).filter(Task.incident_id == incident_id).filter(Task.status == status)
    )


def get_overdue_tasks(*, db_session) -> List[Optional[Task]]:
    """Returns all tasks that have not been resolved and are past due date."""
    # TODO ensure that we don't send reminders more than their interval
    return (
        db_session.query(Task)
        .filter(Task.status == TaskStatus.open)
        .filter(Task.reminders == True)  # noqa
        .filter(Task.resolve_by < datetime.utcnow())
        .filter(
            or_(
                Task.last_reminder_at + timedelta(days=1)
                < datetime.utcnow(),  # daily reminders after due date.
                Task.last_reminder_at == None,
            )
        )
        .all()
    )


def create(
    *,
    db_session,
    creator: str,
    assignees: str,
    description: str,
    status: TaskStatus,
    resource_id: str,
    resource_type: str,
    weblink: str,
) -> Task:
    """Create a new task."""
    task = Task(
        creator=creator,
        assignees=assignees,
        description=description,
        status=status,
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
    )
    db_session.add(task)
    db_session.commit()
    return task


def update(*, db_session, task: Task, task_in: TaskUpdate) -> Task:
    """Update an existing task."""
    task_data = jsonable_encoder(task)
    update_data = task_in.dict(skip_defaults=True)

    for field in task_data:
        if field in update_data:
            setattr(task, field, update_data[field])

    db_session.add(task)
    db_session.commit()
    return task


def delete(*, db_session, task_id: int):
    """Delete an existing task."""
    task = db_session.query(Task).filter(Task.id == task_id).first()
    db_session.delete(task)
    db_session.commit()
