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

from dispatch.database import SessionLocal
from dispatch.messaging import (
    INCIDENT_TASK_REMINDER,
    INCIDENT_TASK_NEW_NOTIFICATION,
    INCIDENT_TASK_RESOLVED_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.task.models import TaskStatus, TaskCreate, TaskUpdate
from dispatch.task import service as task_service


log = logging.getLogger(__name__)


def group_tasks_by_assignee(tasks):
    """Groups tasks by assignee."""
    grouped = defaultdict(lambda: [])
    for task in tasks:
        for a in task.assignees:
            grouped[a.individual.email].append(task)
    return grouped


def create_reminder(db_session, assignee_email, tasks, contact_fullname, contact_weblink):
    """Contains the logic for incident task reminders."""
    # send email
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="email")
    if not plugin:
        log.warning("Task reminder not sent, no email plugin enabled.")
        return

    message_template = INCIDENT_TASK_REMINDER

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

    notification_type = "incident-task-reminder"
    name = subject = "Incident Task Reminder"
    plugin.instance.send(
        assignee_email,
        message_template,
        notification_type,
        name=name,
        subject=subject,
        contact_fullname=contact_fullname,
        contact_weblink=contact_weblink,
        items=items,  # plugin expect dicts
    )

    for task in tasks:
        task.last_reminder_at = datetime.utcnow()
        db_session.commit()


def send_task_notification(
    conversation_id, message_template, assignees, description, weblink, db_session: SessionLocal
):
    """Sends a task notification."""
    # we send a notification to the incident conversation
    notification_text = "Incident Notification"
    notification_type = "incident-notification"
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    plugin.instance.send(
        conversation_id,
        notification_text,
        message_template,
        notification_type,
        task_assignees=[x.individual.email for x in assignees],
        task_description=description,
        task_weblink=weblink,
    )


def create_or_update_task(db_session, incident, task: dict, notify: bool = False):
    """Creates a new task in the database or updates an existing one."""
    existing_task = task_service.get_by_resource_id(
        db_session=db_session, resource_id=task["resource_id"]
    )

    if existing_task:
        # save the status before we attempt to update the record
        existing_status = existing_task.status
        task = task_service.update(
            db_session=db_session, task=existing_task, task_in=TaskUpdate(**task)
        )

        if notify:
            # determine if task was previously resolved
            if task.status == TaskStatus.resolved.value:
                if existing_status != TaskStatus.resolved.value:
                    send_task_notification(
                        incident.conversation.channel_id,
                        INCIDENT_TASK_RESOLVED_NOTIFICATION,
                        task.assignees,
                        task.description,
                        task.weblink,
                        db_session,
                    )
    else:
        task = task_service.create(
            db_session=db_session,
            task_in=TaskCreate(**task, incident=incident),
        )

        if notify:
            send_task_notification(
                incident.conversation.channel_id,
                INCIDENT_TASK_NEW_NOTIFICATION,
                task.assignees,
                task.description,
                task.weblink,
                db_session,
            )

    db_session.commit()
