"""
.. module: dispatch.task.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging

from schedule import every

from dispatch.config import (
    INCIDENT_CONVERSATION_SLUG,
    INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG,
    INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
    INCIDENT_TASK_PLUGIN_SLUG,
    INCIDENT_TASK_SLUG,
)
from dispatch.decorators import background_task
from dispatch.document.service import get_by_incident_id_and_resource_type as get_document
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.messaging import INCIDENT_TASK_NEW_NOTIFICATION, INCIDENT_TASK_RESOLVED_NOTIFICATION
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus

from .flows import create_reminder, group_tasks_by_assignee

TASK_REMINDERS_INTERVAL = 3600  # seconds
TASK_SYNC_INTERVAL = 30  # seconds

log = logging.getLogger(__name__)


@scheduler.add(every(TASK_REMINDERS_INTERVAL).seconds, name="incident-task-reminders")
@background_task
def create_task_reminders(db_session=None):
    """Creates multiple task reminders."""
    tasks = task_service.get_overdue_tasks(db_session=db_session)
    log.debug(f"New tasks that need reminders. NumTasks: {len(tasks)}")
    if tasks:
        grouped_tasks = group_tasks_by_assignee(tasks)
        for assignee, tasks in grouped_tasks.items():
            create_reminder(db_session, assignee, tasks)


@scheduler.add(every(TASK_SYNC_INTERVAL).seconds, name="incident-task-sync")
@background_task
def sync_tasks(db_session=None):
    """Syncs incident tasks."""
    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents

    # we create an instance of the drive task plugin
    drive_task_plugin = plugins.get(INCIDENT_TASK_PLUGIN_SLUG)

    for incident in incidents:
        for doc_type in [
            INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
            INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG,
        ]:
            # we get the document object
            document = get_document(
                db_session=db_session, incident_id=incident.id, resource_type=doc_type
            )

            if not document:
                # the document may have not been created yet (e.g. incident review document)
                break

            # we get the list of tasks in the document
            tasks = drive_task_plugin.list(file_id=document.resource_id)

            for t in tasks:
                # we get the task information
                creator = t["task"]["owner"]
                assignees = ", ".join(t["task"]["assignees"])
                description = t["task"]["description"][0]
                status = TaskStatus.open if not t["task"]["status"] else TaskStatus.resolved
                resource_id = t["task"]["id"]
                weblink = t["task"]["web_link"]

                incident_task = task_service.get_by_resource_id(
                    db_session=db_session, resource_id=t["task"]["id"]
                )
                if incident_task:
                    if status == TaskStatus.open:
                        # we don't need to take any actions if the status of the task in the collaboration doc is open
                        break
                    else:
                        if incident_task.status == TaskStatus.resolved:
                            # we don't need to take any actions if the task has already been marked as resolved in the database
                            break
                        else:
                            # we mark the task as resolved in the database
                            incident_task.status = TaskStatus.resolved
                            db_session.add(incident_task)
                            db_session.commit()

                            # we send a notification to the incident conversation
                            notification_text = "Incident Notification"
                            notification_type = "incident-notification"
                            convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
                            convo_plugin.send(
                                incident.conversation.channel_id,
                                notification_text,
                                INCIDENT_TASK_RESOLVED_NOTIFICATION,
                                notification_type,
                                task_assignees=assignees,
                                task_description=description,
                                task_weblink=weblink,
                            )
                else:
                    # we add the task to the incident
                    task = task_service.create(
                        db_session=db_session,
                        creator=creator,
                        assignees=assignees,
                        description=description,
                        status=status,
                        resource_id=resource_id,
                        resource_type=INCIDENT_TASK_SLUG,
                        weblink=weblink,
                    )
                    incident.tasks.append(task)
                    db_session.add(incident)
                    db_session.commit()

                    # we send a notification to the incident conversation
                    notification_text = "Incident Notification"
                    notification_type = "incident-notification"
                    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
                    convo_plugin.send(
                        incident.conversation.channel_id,
                        notification_text,
                        INCIDENT_TASK_NEW_NOTIFICATION,
                        notification_type,
                        task_assignees=assignees,
                        task_description=description,
                        task_weblink=weblink,
                    )
