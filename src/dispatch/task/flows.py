"""
.. module: dispatch.task.flows
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from collections import defaultdict
from datetime import datetime

from dispatch.database.core import SessionLocal
from dispatch.incident.enums import IncidentStatus
from dispatch.messaging.strings import (
    INCIDENT_TASK_REMINDER,
    INCIDENT_TASK_NEW_NOTIFICATION,
    INCIDENT_TASK_RESOLVED_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.task import service as task_service
from dispatch.task.enums import TaskStatus
from dispatch.task.models import TaskCreate, TaskUpdate


log = logging.getLogger(__name__)


def group_tasks_by_assignee(tasks):
    """Groups tasks by assignee."""
    grouped = defaultdict(lambda: [])
    for task in tasks:
        for a in task.assignees:
            grouped[a.individual.email].append(task)
    return grouped


def create_reminder(db_session, assignee_email, tasks, project_id):
    """Contains the logic for incident task reminders."""
    # send email
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="email", project_id=project_id
    )
    if not plugin:
        log.warning("Task reminder not sent. No email plugin enabled.")
        return

    items = []
    for t in tasks:
        items.append(
            {
                "name": t.incident.name,
                "title": t.incident.title,
                "creator": t.creator.individual.name,
                "description": t.description,
                "priority": t.priority,
                "created_at": t.created_at,
                "resolve_by": t.resolve_by,
                "weblink": t.weblink,
            }
        )

    notification_template = INCIDENT_TASK_REMINDER
    notification_type = "incident-task-reminder"
    name = subject = notification_text = "Incident Task Reminder"

    # Can raise exception "tenacity.RetryError: RetryError". (Email may still go through).
    try:
        plugin.instance.send(
            assignee_email,
            notification_text,
            notification_template,
            notification_type,
            name=name,
            subject=subject,
            items=items,  # plugin expect dicts
        )
    except Exception as e:
        log.error(
            f"Error in sending {notification_text} email to {assignee_email}: {e}. Items: {items}"
        )

    for task in tasks:
        task.last_reminder_at = datetime.utcnow()
        db_session.commit()


def send_task_notification(
    incident,
    message_template,
    creator,
    assignees,
    description,
    weblink,
    db_session: SessionLocal,
):
    """Sends a task notification."""
    # we send a notification to the incident conversation
    notification_text = "Incident Notification"
    notification_type = "incident-notification"

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )

    if not plugin:
        log.warning("Task notification not sent. No conversation plugin enabled.")
        return

    task_assignees = [x.individual.email for x in assignees]

    for assignee in task_assignees:
        plugin.instance.send_ephemeral(
            incident.conversation.channel_id,
            assignee,
            notification_text,
            message_template=message_template,
            notification_type=notification_type,
            task_creator=creator.individual.email,
            task_description=description,
            task_weblink=weblink,
        )


def create_or_update_task(
    db_session, incident, task: dict, notify: bool = False, sync_external: bool = True
):
    """Creates a new task in the database or updates an existing one."""
    existing_task = task_service.get_by_resource_id(
        db_session=db_session, resource_id=task["resource_id"]
    )

    if existing_task:
        # we save the existing task status before we attempt to update the record
        existing_status = existing_task.status
        task = task_service.update(
            db_session=db_session,
            task=existing_task,
            task_in=TaskUpdate(
                **task,
                incident=incident,
            ),
            sync_external=sync_external,
        )

        if notify:
            # determine if task was previously resolved
            if task.status == TaskStatus.resolved:
                if existing_status != TaskStatus.resolved:
                    send_task_notification(
                        incident,
                        INCIDENT_TASK_RESOLVED_NOTIFICATION,
                        task.creator,
                        task.assignees,
                        task.description,
                        task.weblink,
                        db_session,
                    )
    else:
        # we don't attempt to create new tasks if the incident is currently closed
        if incident.status == IncidentStatus.closed:
            return

        task = task_service.create(
            db_session=db_session,
            task_in=TaskCreate(**task, incident=incident),
        )

        if notify:
            send_task_notification(
                incident,
                INCIDENT_TASK_NEW_NOTIFICATION,
                task.creator,
                task.assignees,
                task.description,
                task.weblink,
                db_session,
            )

    db_session.commit()
