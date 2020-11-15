from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import or_

from dispatch.plugin import service as plugin_service
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident.flows import incident_service
from dispatch.ticket import service as ticket_service
from .models import Task, TaskStatus, TaskUpdate, TaskCreate


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


def create(*, db_session, task_in: TaskCreate) -> Task:
    """Create a new task."""
    incident = incident_service.get(db_session=db_session, incident_id=task_in.incident.id)
    tickets = [
        ticket_service.get_or_create_by_weblink(
            db_session=db_session, weblink=t.weblink, resource_type="task-ticket"
        )
        for t in task_in.tickets
    ]

    assignees = []
    for i in task_in.assignees:
        assignee = incident_flows.incident_add_or_reactivate_participant_flow(
            db_session=db_session,
            incident_id=incident.id,
            user_email=i.individual.email,
        )

        # due to the freeform nature of task assignment, we can sometimes pick up other emails
        # e.g. a google group that we cannont resolve to an individual assignee
        if assignee:
            assignees.append(assignee)

    creator_email = None
    if not task_in.creator:
        creator_email = task_in.owner.individual.email
    else:
        creator_email = task_in.creator.individual.email

    # add creator as a participant if they are not one already
    creator = incident_flows.incident_add_or_reactivate_participant_flow(
        db_session=db_session,
        incident_id=incident.id,
        user_email=creator_email,
    )

    # if we cannot find any assignees, the creator becomes the default assignee
    if not assignees:
        assignees.append(creator)

    # we add owner as a participant if they are not one already
    if task_in.owner:
        owner = incident_flows.incident_add_or_reactivate_participant_flow(
            db_session=db_session,
            incident_id=incident.id,
            user_email=task_in.owner.individual.email,
        )
    else:
        owner = incident.commander

    task = Task(
        **task_in.dict(exclude={"assignees", "owner", "incident", "creator", "tickets"}),
        creator=creator,
        owner=owner,
        assignees=assignees,
        incident=incident,
        tickets=tickets,
    )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="New incident task created",
        details={"weblink": task.weblink},
        incident_id=incident.id,
    )

    db_session.add(task)
    db_session.commit()
    return task


def update(*, db_session, task: Task, task_in: TaskUpdate) -> Task:
    """Update an existing task."""
    # ensure we add assignee as participant if they are not one already
    assignees = []
    for i in task_in.assignees:
        assignees.append(
            incident_flows.incident_add_or_reactivate_participant_flow(
                db_session=db_session,
                incident_id=task.incident.id,
                user_email=i.individual.email,
            )
        )

    task.assignees = assignees

    # we add owner as a participant if they are not one already
    if task_in.owner:
        task.owner = incident_flows.incident_add_or_reactivate_participant_flow(
            db_session=db_session,
            incident_id=task.incident.id,
            user_email=task_in.owner.individual.email,
        )

    update_data = task_in.dict(
        skip_defaults=True, exclude={"assignees", "owner", "creator", "incident", "tickets"}
    )

    for field in update_data.keys():
        setattr(task, field, update_data[field])

    # if we have an external task plugin enabled, attempt to update the external resource as well
    # we don't currently have a good way to get the correct file_id (we don't store a task <-> relationship)
    # lets try in both the incident doc and PIR doc
    drive_task_plugin = plugin_service.get_active(db_session=db_session, plugin_type="task")

    if drive_task_plugin:
        try:
            file_id = task.incident.incident_document.resource_id
            drive_task_plugin.instance.update(file_id, task.external_task_id, resolved=task.status)
        except Exception:
            file_id = task.incident.incident_review_document.resource_id
            drive_task_plugin.instance.update(file_id, task.external_task_id, resolved=task.status)

    db_session.add(task)
    db_session.commit()
    return task


def delete(*, db_session, task_id: int):
    """Delete an existing task."""
    task = db_session.query(Task).filter(Task.id == task_id).first()
    db_session.delete(task)
    db_session.commit()
