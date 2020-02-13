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

from dispatch.config import INCIDENT_PLUGIN_EMAIL_SLUG
from dispatch.messaging import INCIDENT_TASK_REMINDER
from dispatch.plugins.base import plugins

log = logging.getLogger(__name__)


def group_tasks_by_assignee(tasks):
    """Groups tasks by assignee."""
    grouped = defaultdict(lambda: [])
    for task in tasks:
        grouped[task.assignees].append(task)
    return grouped


def create_reminder(db_session, assignee, tasks):
    """Contains the logic for incident task reminders."""
    # send email
    email_plugin = plugins.get(INCIDENT_PLUGIN_EMAIL_SLUG)
    message_template = INCIDENT_TASK_REMINDER

    notification_type = "incident-task-reminder"
    email_plugin.send(
        assignee, message_template, notification_type, name="Task Reminder", items=tasks
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
