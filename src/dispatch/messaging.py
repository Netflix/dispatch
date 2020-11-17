import copy
from enum import Enum

from jinja2 import Template

from typing import List

from dispatch.conversation.enums import ConversationButtonActions
from dispatch.incident.enums import IncidentStatus

from .config import (
    INCIDENT_RESOURCE_CONVERSATION_REFERENCE_DOCUMENT,
    INCIDENT_RESOURCE_EXECUTIVE_REPORT_DOCUMENT,
    INCIDENT_RESOURCE_INCIDENT_FAQ_DOCUMENT,
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_SHEET,
)


class MessageType(str, Enum):
    incident_closed_information_review_reminder = "incident-closed-information-review-reminder"
    incident_daily_summary = "incident-daily-summary"
    incident_daily_summary_no_incidents = "incident-daily-summary-no-incidents"
    incident_executive_report = "incident-executive-report"
    incident_notification = "incident-notification"
    incident_participant_suggested_reading = "incident-participant-suggested-reading"
    incident_participant_welcome = "incident-participant-welcome"
    incident_rating_feedback = "incident-rating-feedback"
    incident_resources_message = "incident-resources-message"
    incident_status_reminder = "incident-status-reminder"
    incident_tactical_report = "incident-tactical-report"
    incident_task_list = "incident-task-list"
    incident_task_reminder = "incident-task-reminder"
    document_evergreen_reminder = "document-evergreen-reminder"


INCIDENT_STATUS_DESCRIPTIONS = {
    IncidentStatus.active: "This incident is under active investigation.",
    IncidentStatus.stable: "This incident is stable, the bulk of the investigation has been completed or most of the risk has been mitigated.",
    IncidentStatus.closed: "This no longer requires additional involvement, long term incident action items have been assigned to their respective owners.",
}

INCIDENT_TASK_REMINDER_DESCRIPTION = """
You are assigned to the following incident tasks.
This is a reminder that these tasks have passed their due date.
Please review and update them as appropriate. Resolving them will stop the reminders.""".replace(
    "\n", " "
).strip()

INCIDENT_TASK_LIST_DESCRIPTION = """The following are open incident tasks."""

DOCUMENT_EVERGREEN_REMINDER_DESCRIPTION = """
You are the owner of the following incident documents.
This is a reminder that these documents should be kept up to date in order to effectively
respond to incidents. Please review them and update, or clearly mark the documents as deprecated.""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_SUMMARY_DESCRIPTION = """
Daily Incidents Summary""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_SUMMARY_ACTIVE_INCIDENTS_DESCRIPTION = """
Active Incidents""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_SUMMARY_NO_ACTIVE_INCIDENTS_DESCRIPTION = """
There are no active incidents at this moment.""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_SUMMARY_STABLE_CLOSED_INCIDENTS_DESCRIPTION = """
Stable or Closed Incidents (last 24 hours)""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_SUMMARY_NO_STABLE_CLOSED_INCIDENTS_DESCRIPTION = """
There are no stable or closed incidents in the last 24 hours.""".replace(
    "\n", " "
).strip()

INCIDENT_COMMANDER_DESCRIPTION = """
The Incident Commander (IC) is responsible for
knowing the full context of the incident.
Contact them about any questions or concerns.""".replace(
    "\n", " "
).strip()

INCIDENT_COMMANDER_READDED_DESCRIPTION = """
{{ commander_fullname }} (Incident Commander) has been re-added to the conversation.
Please, handoff the Incident Commander role before leaving the conversation.""".replace(
    "\n", " "
).strip()

INCIDENT_TICKET_DESCRIPTION = """
Ticket for tracking purposes. It contains a description of
the incident and links to resources.""".replace(
    "\n", " "
).strip()

INCIDENT_CONVERSATION_DESCRIPTION = """
Private conversation for real-time discussion. All incident participants get added to it.
""".replace(
    "\n", " "
).strip()

INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION = """
Document containing the list of slash commands available to the Incident Commander (IC)
and participants in the incident conversation.""".replace(
    "\n", " "
).strip()

INCIDENT_CONFERENCE_DESCRIPTION = """
Video conference and phone bridge to be used throughout the incident.  Password: {{conference_challenge if conference_challenge else 'N/A'}}
""".replace(
    "\n", ""
).strip()

INCIDENT_STORAGE_DESCRIPTION = """
Common storage for all incident artifacts and
documents. Add logs, screen captures, or any other data collected during the
investigation to this drive. It is shared with all incident participants.""".replace(
    "\n", " "
).strip()

INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION = """
This is a document for all incident facts and context. All
incident participants are expected to contribute to this document.
It is shared with all incident participants.""".replace(
    "\n", " "
).strip()

INCIDENT_INVESTIGATION_SHEET_DESCRIPTION = """
This is a sheet for tracking impacted assets. All
incident participants are expected to contribute to this sheet.
It is shared with all incident participants.""".replace(
    "\n", " "
).strip()

INCIDENT_FAQ_DOCUMENT_DESCRIPTION = """
First time responding to an information security incident? This
document answers common questions encountered when
helping us respond to an incident.""".replace(
    "\n", " "
).strip()

INCIDENT_REVIEW_DOCUMENT_DESCRIPTION = """
This document will capture all lessons learned, questions, and action items raised during the incident.""".replace(
    "\n", " "
).strip()

INCIDENT_EXECUTIVE_REPORT_DOCUMENT_DESCRIPTION = """
This is a document that contains an executive report about the incident.""".replace(
    "\n", " "
).strip()

INCIDENT_DOCUMENT_DESCRIPTIONS = {
    INCIDENT_RESOURCE_CONVERSATION_REFERENCE_DOCUMENT: INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION,
    INCIDENT_RESOURCE_EXECUTIVE_REPORT_DOCUMENT: INCIDENT_EXECUTIVE_REPORT_DOCUMENT_DESCRIPTION,
    INCIDENT_RESOURCE_INCIDENT_FAQ_DOCUMENT: INCIDENT_FAQ_DOCUMENT_DESCRIPTION,
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT: INCIDENT_REVIEW_DOCUMENT_DESCRIPTION,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT: INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION,
    INCIDENT_RESOURCE_INVESTIGATION_SHEET: INCIDENT_INVESTIGATION_SHEET_DESCRIPTION,
}

INCIDENT_PARTICIPANT_WELCOME_DESCRIPTION = """
You\'re being contacted because we think you may
be able to help us during this information security incident.
Please review the content below and join us in the
incident Slack channel.""".replace(
    "\n", " "
).strip()

INCIDENT_WELCOME_CONVERSATION_COPY = """
This is the incident conversation. Please pull in any
individuals you feel may be able to help resolve this incident.""".replace(
    "\n", " "
).strip()

INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION = """
Dispatch thinks the following documents might be
relevant to this incident.""".replace(
    "\n", " "
).strip()

INCIDENT_NOTIFICATION_PURPOSES_FYI = """
This message is for notification purposes only.""".replace(
    "\n", " "
).strip()

INCIDENT_CAN_REPORT_REMINDER = """
It's time to send a new CAN report. Go to the Demisto UI and run the
CAN Report playbook from the Playground Work Plan.""".replace(
    "\n", " "
).strip()

INCIDENT_VULNERABILITY_DESCRIPTION = """
We are tracking the details of the vulnerability that led to this incident
in the VUL Jira issue linked above.""".replace(
    "\n", " "
).strip()

INCIDENT_STABLE_DESCRIPTION = """
The risk has been contained and the incident marked as stable.""".replace(
    "\n", " "
).strip()

INCIDENT_CLOSED_DESCRIPTION = """
The incident has been resolved and marked as closed.""".replace(
    "\n", " "
).strip()

INCIDENT_TACTICAL_REPORT_DESCRIPTION = """
The following conditions, actions, and needs summarize the current status of the incident.""".replace(
    "\n", " "
).strip()

INCIDENT_NEW_ROLE_DESCRIPTION = """
{{assigner_fullname if assigner_fullname else assigner_email}} has assigned the role of {{assignee_role}} to {{assignee_fullname if assignee_fullname else assignee_email}}.
Please, contact {{assignee_fullname if assignee_fullname else assignee_email}} about any questions or concerns.""".replace(
    "\n", " "
).strip()

INCIDENT_REPORT_REMINDER_DESCRIPTION = """You have not provided a {{report_type}} for this incident recently.
You can use `{{command}}` in the conversation to assist you in writing one.""".replace(
    "\n", " "
).strip()

INCIDENT_STATUS_REMINDER_DESCRIPTION = """You have not updated the status for this incident recently. If the incident has been resolved,
you can use `{{command}}` in the conversation to assist you in closing your incident.""".replace(
    "\n", " "
).strip()

INCIDENT_TASK_NEW_DESCRIPTION = """
The following incident task has been created in the incident document.\n\n*Description:* {{task_description}}\n\n*Assignees:* {{task_assignees|join(',')}}"""

INCIDENT_TASK_RESOLVED_DESCRIPTION = """
The following incident task has been resolved in the incident document.\n\n*Description:* {{task_description}}\n\n*Assignees:* {{task_assignees|join(',')}}"""

INCIDENT_WORKFLOW_CREATED_DESCRIPTION = """
A new workflow instance has been created.
\n\n *Creator:* {{instance_creator_name}}
"""

INCIDENT_WORKFLOW_UPDATE_DESCRIPTION = """
This workflow's status has changed from *{{ instance_status_old }}* to *{{ instance_status_new }}*.
\n\n*Workflow Description*: {{workflow_description}}
\n\n *Creator:* {{instance_creator_name}}
"""

INCIDENT_WORKFLOW_COMPLETE_DESCRIPTION = """
This workflow's status has changed from *{{ instance_status_old }}* to *{{ instance_status_new }}*.
\n\n *Workflow Description:* {{workflow_description}}
\n\n *Creator:* {{instance_creator_name}}
{% if instance_artifacts %}
\n\n *Workflow Artifacts:*
\n\n {% for a in instance_artifacts %}- <{{a.weblink}}|{{a.name}}> \n\n{% endfor %}
{% endif %}
"""

INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_DESCRIPTION = """
Thanks for closing incident {{name}}. Please take a minute to review the following incident data:
\n - *Title:* {{title}}
\n - *Description:* {{description}}
\n - *Incident Type:* {{type}}
\n - *Incident Priority:* {{priority}}
\n\n
Is the information up to date? If not, please edit the incident in the <{{dispatch_ui_url}}|Dispatch Web UI>.
\n\n
Also please be sure to take the following actions:
\n - Update or add any relevant incident tags using the <{{dispatch_ui_url}}|Dispatch Web UI>.
\n - Review and close any incident tasks that are no longer relevant/required.
"""

INCIDENT_CLOSED_RATING_FEEDBACK_DESCRIPTION = """
Thanks for participating in the {{name}} ("{{title}}") incident. We would appreciate if you could rate your experience and provide feedback."""

INCIDENT_TYPE_CHANGE_DESCRIPTION = """
The incident type has been changed from *{{ incident_type_old }}* to *{{ incident_type_new }}*."""

INCIDENT_STATUS_CHANGE_DESCRIPTION = """
The incident status has been changed from *{{ incident_status_old }}* to *{{ incident_status_new }}*."""

INCIDENT_PRIORITY_CHANGE_DESCRIPTION = """
The incident priority has been changed from *{{ incident_priority_old }}* to *{{ incident_priority_new }}*."""

INCIDENT_NAME_WITH_ENGAGEMENT = {
    "title": "{{name}} Incident Notification",
    "title_link": "{{ticket_weblink}}",
    "text": INCIDENT_NOTIFICATION_PURPOSES_FYI,
    "button_text": "Join Incident",
    "button_value": "{{incident_id}}",
    "button_action": ConversationButtonActions.invite_user,
}

INCIDENT_NAME = {
    "title": "{{name}} Incident Notification",
    "title_link": "{{ticket_weblink}}",
    "text": INCIDENT_NOTIFICATION_PURPOSES_FYI,
}

INCIDENT_TITLE = {"title": "Incident Title", "text": "{{title}}"}

INCIDENT_DESCRIPTION = {"title": "Incident Description", "text": "{{description}}"}

INCIDENT_STATUS = {
    "title": "Incident Status - {{status}}",
    "status_mapping": INCIDENT_STATUS_DESCRIPTIONS,
}

INCIDENT_TYPE = {"title": "Incident Type - {{type}}", "text": "{{type_description}}"}

INCIDENT_PRIORITY = {
    "title": "Incident Priority - {{priority}}",
    "text": "{{priority_description}}",
}

INCIDENT_PRIORITY_FYI = {
    "title": "Incident Priority - {{priority}}",
    "text": "{{priority_description}}",
}

INCIDENT_COMMANDER = {
    "title": "Incident Commander - {{commander_fullname}}",
    "title_link": "{{commander_weblink}}",
    "text": INCIDENT_COMMANDER_DESCRIPTION,
}

INCIDENT_CONFERENCE = {
    "title": "Incident Conference",
    "title_link": "{{conference_weblink}}",
    "text": INCIDENT_CONFERENCE_DESCRIPTION,
}

INCIDENT_STORAGE = {
    "title": "Incident Storage",
    "title_link": "{{storage_weblink}}",
    "text": INCIDENT_STORAGE_DESCRIPTION,
}

INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT = {
    "title": "Incident Conversation Commands Reference Document",
    "title_link": "{{conversation_commands_reference_document_weblink}}",
    "text": INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION,
}

INCIDENT_INVESTIGATION_DOCUMENT = {
    "title": "Incident Investigation Document",
    "title_link": "{{document_weblink}}",
    "text": INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION,
}

INCIDENT_INVESTIGATION_SHEET = {
    "title": "Incident Investigation Sheet",
    "title_link": "{{sheet_weblink}}",
    "text": INCIDENT_INVESTIGATION_SHEET_DESCRIPTION,
}

INCIDENT_REVIEW_DOCUMENT = {
    "title": "Incident Review Document",
    "title_link": "{{review_document_weblink}}",
    "text": INCIDENT_REVIEW_DOCUMENT_DESCRIPTION,
}

INCIDENT_FAQ_DOCUMENT = {
    "title": "Incident FAQ Document",
    "title_link": "{{faq_weblink}}",
    "text": INCIDENT_FAQ_DOCUMENT_DESCRIPTION,
}

INCIDENT_TYPE_CHANGE = {"title": "Incident Type Change", "text": INCIDENT_TYPE_CHANGE_DESCRIPTION}

INCIDENT_STATUS_CHANGE = {
    "title": "Incident Status Change",
    "text": INCIDENT_STATUS_CHANGE_DESCRIPTION,
}

INCIDENT_PRIORITY_CHANGE = {
    "title": "Incident Priority Change",
    "text": INCIDENT_PRIORITY_CHANGE_DESCRIPTION,
}

INCIDENT_PARTICIPANT_SUGGESTED_READING_ITEM = {
    "title": "{{name}}",
    "title_link": "{{weblink}}",
    "text": "{{description}}",
}

INCIDENT_PARTICIPANT_WELCOME = {
    "title": "Welcome to {{name}}",
    "title_link": "{{ticket_weblink}}",
    "text": INCIDENT_PARTICIPANT_WELCOME_DESCRIPTION,
}

INCIDENT_PARTICIPANT_WELCOME_MESSAGE = [
    INCIDENT_PARTICIPANT_WELCOME,
    INCIDENT_TITLE,
    INCIDENT_STATUS,
    INCIDENT_TYPE,
    INCIDENT_PRIORITY,
    INCIDENT_COMMANDER,
    INCIDENT_INVESTIGATION_DOCUMENT,
    INCIDENT_STORAGE,
    INCIDENT_CONFERENCE,
    INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
    INCIDENT_FAQ_DOCUMENT,
]

INCIDENT_RESOURCES_MESSAGE = [
    INCIDENT_COMMANDER,
    INCIDENT_INVESTIGATION_DOCUMENT,
    INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_STORAGE,
    INCIDENT_CONFERENCE,
    INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
    INCIDENT_FAQ_DOCUMENT,
]

INCIDENT_NOTIFICATION_COMMON = [INCIDENT_TITLE]

INCIDENT_NOTIFICATION = INCIDENT_NOTIFICATION_COMMON.copy()
INCIDENT_NOTIFICATION.extend(
    [INCIDENT_STATUS, INCIDENT_TYPE, INCIDENT_PRIORITY_FYI, INCIDENT_COMMANDER]
)

INCIDENT_TACTICAL_REPORT = [
    {"title": "Incident Tactical Report", "text": INCIDENT_TACTICAL_REPORT_DESCRIPTION},
    {"title": "Conditions", "text": "{{conditions}}"},
    {"title": "Actions", "text": "{{actions}}"},
    {"title": "Needs", "text": "{{needs}}"},
]

INCIDENT_EXECUTIVE_REPORT = [
    {"title": "Incident Title", "text": "{{title}}"},
    {"title": "Current Status", "text": "{{current_status}}"},
    {"title": "Overview", "text": "{{overview}}"},
    {"title": "Next Steps", "text": "{{next_steps}}"},
]

INCIDENT_REPORT_REMINDER = [
    {
        "title": "{{name}} Incident - {{report_type}} Reminder",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_REPORT_REMINDER_DESCRIPTION,
    },
    INCIDENT_TITLE,
]


INCIDENT_STATUS_REMINDER = [
    {
        "title": "{{name}} Incident - Status Reminder",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_STATUS_REMINDER_DESCRIPTION,
    },
    INCIDENT_TITLE,
    INCIDENT_STATUS,
]

INCIDENT_TASK_REMINDER = [
    {"title": "Incident - {{ name }}", "text": "{{ title }}"},
    {"title": "Creator", "text": "{{ creator }}"},
    {"title": "Description", "text": "{{ description }}"},
    {"title": "Priority", "text": "{{ priority }}"},
    {"title": "Created At", "text": "", "datetime": "{{ created_at}}"},
    {"title": "Resolve By", "text": "", "datetime": "{{ resolve_by }}"},
    {"title": "Link", "text": "{{ weblink }}"},
]

DOCUMENT_EVERGREEN_REMINDER = [
    {"title": "Document", "text": "{{ name }}"},
    {"title": "Description", "text": "{{ description }}"},
    {"title": "Link", "text": "{{ weblink }}"},
]

INCIDENT_NEW_ROLE_NOTIFICATION = [
    {
        "title": "New {{assignee_role}} - {{assignee_fullname if assignee_fullname else assignee_email}}",
        "title_link": "{{assignee_weblink}}",
        "text": INCIDENT_NEW_ROLE_DESCRIPTION,
    }
]

INCIDENT_TASK_NEW_NOTIFICATION = [
    {
        "title": "New Incident Task",
        "title_link": "{{task_weblink}}",
        "text": INCIDENT_TASK_NEW_DESCRIPTION,
    }
]

INCIDENT_TASK_RESOLVED_NOTIFICATION = [
    {
        "title": "Resolved Incident Task",
        "title_link": "{{task_weblink}}",
        "text": INCIDENT_TASK_RESOLVED_DESCRIPTION,
    }
]

INCIDENT_WORKFLOW_CREATED_NOTIFICATION = [
    {
        "title": "Workflow Created - {{workflow_name}}",
        "text": INCIDENT_WORKFLOW_CREATED_DESCRIPTION,
    }
]

INCIDENT_WORKFLOW_UPDATE_NOTIFICATION = [
    {
        "title": "Workflow Status Change - {{workflow_name}}",
        "title_link": "{{instance_weblink}}",
        "text": INCIDENT_WORKFLOW_UPDATE_DESCRIPTION,
    }
]

INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION = [
    {
        "title": "Workflow Completed - {{workflow_name}}",
        "title_link": "{{instance_weblink}}",
        "text": INCIDENT_WORKFLOW_COMPLETE_DESCRIPTION,
    }
]

INCIDENT_COMMANDER_READDED_NOTIFICATION = [
    {"title": "Incident Commander Re-Added", "text": INCIDENT_COMMANDER_READDED_DESCRIPTION}
]

INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_NOTIFICATION = [
    {
        "title": "{{name}} Incident - Information Review Reminder",
        "title_link": "{{dispatch_ui_url}}",
        "text": INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_DESCRIPTION,
    }
]

INCIDENT_CLOSED_RATING_FEEDBACK_NOTIFICATION = [
    {
        "title": "{{name}} Incident - Rating and Feedback",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_CLOSED_RATING_FEEDBACK_DESCRIPTION,
        "button_text": "Provide Feeback",
        "button_value": "{{incident_id}}",
        "button_action": ConversationButtonActions.provide_feedback,
    }
]


def render_message_template(message_template: List[dict], **kwargs):
    """Renders the jinja data included in the template itself."""
    data = []
    new_copy = copy.deepcopy(message_template)
    for d in new_copy:
        if d.get("status_mapping"):
            d["text"] = d["status_mapping"][kwargs["status"]]

        if d.get("datetime"):
            d["datetime"] = Template(d["datetime"]).render(**kwargs)

        d["text"] = Template(d["text"]).render(**kwargs)
        d["title"] = Template(d["title"]).render(**kwargs)

        if d.get("title_link"):
            d["title_link"] = Template(d["title_link"]).render(**kwargs)

            if d["title_link"] == "None":  # skip blocks with no content
                continue

            # skip blocks that do not have new links rendered, as no real value was provided
            if not d["title_link"]:
                continue

        if d.get("button_text"):
            d["button_text"] = Template(d["button_text"]).render(**kwargs)

        if d.get("button_value"):
            d["button_value"] = Template(d["button_value"]).render(**kwargs)

        data.append(d)
    return data
