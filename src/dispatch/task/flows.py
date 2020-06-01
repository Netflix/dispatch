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

from dispatch.config import (
    INCIDENT_PLUGIN_EMAIL_SLUG,
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_RESOURCE_INCIDENT_TASK,
)
from dispatch.messaging import (
    INCIDENT_TASK_REMINDER,
    INCIDENT_TASK_NEW_NOTIFICATION,
    INCIDENT_TASK_RESOLVED_NOTIFICATION,
)
from dispatch.plugins.base import plugins
from dispatch.incident.flows import incident_add_or_reactivate_participant_flow
from dispatch.task.models import TaskStatus
from dispatch.task import service as task_service
from dispatch.ticket import service as ticket_service


log = logging.getLogger(__name__)


def group_tasks_by_assignee(tasks):
    """Groups tasks by assignee."""
    grouped = defaultdict(lambda: [])
    for task in tasks:
        for a in task.assignees:
            grouped[a.individual.email].append(task)
    return grouped


def create_reminder(db_session, assignee_email, tasks):
    """Contains the logic for incident task reminders."""
    # send email
    email_plugin = plugins.get(INCIDENT_PLUGIN_EMAIL_SLUG)
    message_template = INCIDENT_TASK_REMINDER

    items = []
    for t in tasks:
        items.append(
            {
                "name": t.incident.name,
                "title": t.incident.title,
                "creator": t.creator.individual.name,
                "priority": t.priority,
                "created_at": t.created_at,
                "resolve_by": t.resolve_by,
                "weblink": t.weblink,
            }
        )

    notification_type = "incident-task-reminder"
    email_plugin.send(
        assignee_email,
        message_template,
        notification_type,
        name="Task Reminder",
        items=items,  # plugin expect dicts
    )

    # We currently think DM's might be too agressive
    # send slack
    # convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    # convo_plugin.send_direct(
    #    assignee, notification_text, message_template, notification_type, items=tasks
    # )

    for task in tasks:
        task.last_reminder_at = datetime.utcnow()
        db_session.commit()


def send_task_notification(conversation_id, message_template, assignees, description, weblink):
    """Sends a task notification."""
    # we send a notification to the incident conversation
    notification_text = "Incident Notification"
    notification_type = "incident-notification"
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
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
    incident_task = task_service.get_by_resource_id(db_session=db_session, resource_id=task["id"])

    assignees = []
    for a in task["assignees"]:
        assignees.append(
            db_session.merge(
                incident_add_or_reactivate_participant_flow(
                    a, incident_id=incident.id, db_session=db_session
                )
            )
        )

    description = task["description"][0]
    status = TaskStatus.open if not task["status"] else TaskStatus.resolved
    resource_id = task["id"]
    weblink = task["web_link"]

    # TODO we can build this out as our scraping gets more advanced
    tickets = [
        ticket_service.get_or_create_by_weblink(db_session=db_session, weblink=t["web_link"])
        for t in task["tickets"]
    ]

    if incident_task:
        # allways update tickets and assignees
        incident_task.assignees = assignees
        incident_task.tickets = tickets

        # only notify if it's newly resolved
        if status == TaskStatus.resolved:
            if incident_task.status != TaskStatus.resolved:
                incident_task.status = status

                if notify:
                    send_task_notification(
                        incident.conversation.channel_id,
                        INCIDENT_TASK_RESOLVED_NOTIFICATION,
                        assignees,
                        description,
                        weblink,
                    )

    else:
        # we add the task to the incident
        creator = incident_add_or_reactivate_participant_flow(
            task["owner"], incident_id=incident.id, db_session=db_session
        )

        task = task_service.create(
            db_session=db_session,
            creator=creator,
            assignees=assignees,
            description=description,
            status=status,
            tickets=tickets,
            resource_id=resource_id,
            resource_type=INCIDENT_RESOURCE_INCIDENT_TASK,
            weblink=weblink,
        )
        incident.tasks.append(task)

        if notify:
            send_task_notification(
                incident.conversation.channel_id,
                INCIDENT_TASK_NEW_NOTIFICATION,
                assignees,
                description,
                weblink,
            )

    db_session.commit()
