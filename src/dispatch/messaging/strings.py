import copy

from typing import List, Optional

from dispatch.messaging.email.filters import env
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.incident.enums import IncidentStatus
from dispatch.case.enums import CaseStatus
from dispatch.enums import Visibility
from dispatch.email_templates.models import EmailTemplates

from dispatch import config
from dispatch.enums import DispatchEnum, DocumentResourceTypes, DocumentResourceReferenceTypes

"""Dict for reminder strings and values. Note values are in hours"""
reminder_select_values = {
    "thirty": {"message": "30 minutes", "value": 0.5},
    "one_hour": {"message": "1 hour", "value": 1},
    "two_hours": {"message": "2 hours", "value": 2},
}


class MessageType(DispatchEnum):
    evergreen_reminder = "evergreen-reminder"
    incident_closed_information_review_reminder = "incident-closed-information-review-reminder"
    incident_completed_form_notification = "incident-completed-form-notification"
    incident_daily_report = "incident-daily-report"
    incident_executive_report = "incident-executive-report"
    incident_feedback_daily_report = "incident-feedback-daily-report"
    incident_management_help_tips = "incident-management-help-tips"
    incident_notification = "incident-notification"
    incident_open_tasks = "incident-open-tasks"
    incident_participant_suggested_reading = "incident-participant-suggested-reading"
    incident_participant_welcome = "incident-participant-welcome"
    incident_rating_feedback = "incident-rating-feedback"
    incident_status_reminder = "incident-status-reminder"
    incident_tactical_report = "incident-tactical-report"
    incident_task_list = "incident-task-list"
    incident_task_reminder = "incident-task-reminder"
    case_notification = "case-notification"
    case_status_reminder = "case-status-reminder"
    service_feedback = "service-feedback"
    task_add_to_incident = "task-add-to-incident"


INCIDENT_STATUS_DESCRIPTIONS = {
    IncidentStatus.active: "This incident is under active investigation.",
    IncidentStatus.stable: "This incident is stable, the bulk of the investigation has been completed or most of the risk has been mitigated.",
    IncidentStatus.closed: "This no longer requires additional involvement, long term incident action items have been assigned to their respective owners.",
}

CASE_STATUS_DESCRIPTIONS = {
    CaseStatus.new: "This case is new and needs triaging.",
    CaseStatus.triage: "This case is being triaged.",
    CaseStatus.escalated: "This case has been escalated.",
    CaseStatus.closed: "This case has been closed.",
}

INCIDENT_VISIBILITY_DESCRIPTIONS = {
    Visibility.open: "We ask that you use your best judgment while sharing details about this incident outside of the dedicated channels of communication. Please reach out to the Incident Commander if you have any questions.",
    Visibility.restricted: "This incident is restricted to immediate participants of this incident. We ask that you exercise extra caution and discretion while talking about this incident outside of the dedicated channels of communication. Only invite new participants that are strictly necessary. Please reach out to the Incident Commander if you have any questions.",
}

CASE_VISIBILITY_DESCRIPTIONS = {
    Visibility.open: "We ask that you use your best judgment while sharing details about this case outside of the dedicated channels of communication. Please reach out to the case assignee if you have any questions.",
    Visibility.restricted: "This case is restricted to immediate participants of this case. We ask that you exercise extra caution and discretion while talking about this case outside of the dedicated channels of communication. Only invite new participants that are strictly necessary. Please reach out to the case assignee if you have any questions.",
}

EVERGREEN_REMINDER_DESCRIPTION = """
You are the owner of the following resources in Dispatch.
This is a reminder that these resources should be kept up to date in order to effectively
respond to incidents. Please review and update them, or mark them as deprecated.""".replace(
    "\n", " "
).strip()

INCIDENT_FEEDBACK_DAILY_REPORT_DESCRIPTION = """
This is a daily report of feedback about incidents handled by you.""".replace("\n", " ").strip()

INCIDENT_DAILY_REPORT_TITLE = """
Incidents Daily Report""".replace("\n", " ").strip()

INCIDENT_DAILY_REPORT_DESCRIPTION = """
This is a daily report of incidents that are currently active and incidents that have been marked as stable or closed in the last 24 hours.""".replace(
    "\n", " "
).strip()

INCIDENT_DAILY_REPORT_FOOTER_CONTEXT = """
For questions about an incident, please reach out to the incident's commander.""".replace(
    "\n", " "
).strip()

INCIDENT_REPORTER_DESCRIPTION = """
The person who reported the incident. Contact them if the report details need clarification.""".replace(
    "\n", " "
).strip()

INCIDENT_COMMANDER_DESCRIPTION = """
The Incident Commander (IC) is responsible for
knowing the full context of the incident.
Contact them about any questions or concerns.""".replace("\n", " ").strip()

INCIDENT_COMMANDER_READDED_DESCRIPTION = """
{{ commander_fullname }} (Incident Commander) has been re-added to the conversation.
Please, handoff the Incident Commander role before leaving the conversation.""".replace(
    "\n", " "
).strip()

TICKET_DESCRIPTION = """
Ticket for tracking purposes. It contains information and links to resources.""".replace(
    "\n", " "
).strip()

TACTICAL_GROUP_DESCRIPTION = """
Group for managing member access to storage. All participants get added to it.""".replace(
    "\n", " "
).strip()

NOTIFICATIONS_GROUP_DESCRIPTION = """
Group for email notification purposes. All participants get added to it.""".replace(
    "\n", " "
).strip()

INCIDENT_CONVERSATION_DESCRIPTION = """
Private conversation for real-time discussion. All incident participants get added to it.
""".replace("\n", " ").strip()

INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION = """
Document containing the list of slash commands available to the Incident Commander (IC)
and participants in the incident conversation.""".replace("\n", " ").strip()

INCIDENT_CONFERENCE_DESCRIPTION = """
Video conference and phone bridge to be used throughout the incident.  Password: {{conference_challenge if conference_challenge else 'N/A'}}
""".replace("\n", "").strip()

STORAGE_DESCRIPTION = """
Common storage for all artifacts and
documents. Add logs, screen captures, or any other data collected during the
investigation to this folder. It is shared with all participants.""".replace("\n", " ").strip()

INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION = """
This is a document for all incident facts and context. All
incident participants are expected to contribute to this document.
It is shared with all incident participants.""".replace("\n", " ").strip()

CASE_INVESTIGATION_DOCUMENT_DESCRIPTION = """
This is a document for all investigation facts and context. All
case participants are expected to contribute to this document.
It is shared with all participants.""".replace("\n", " ").strip()

INCIDENT_INVESTIGATION_SHEET_DESCRIPTION = """
This is a sheet for tracking impacted assets. All
incident participants are expected to contribute to this sheet.
It is shared with all incident participants.""".replace("\n", " ").strip()

INCIDENT_FAQ_DOCUMENT_DESCRIPTION = """
First time responding to an incident? This
document answers common questions encountered when
helping us respond to an incident.""".replace("\n", " ").strip()

INCIDENT_REVIEW_DOCUMENT_DESCRIPTION = """
This document will capture all lessons learned, questions, and action items raised during the incident.""".replace(
    "\n", " "
).strip()

INCIDENT_EXECUTIVE_REPORT_DOCUMENT_DESCRIPTION = """
This is a document that contains an executive report about the incident.""".replace(
    "\n", " "
).strip()

DOCUMENT_DESCRIPTIONS = {
    DocumentResourceReferenceTypes.conversation: INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION,
    DocumentResourceReferenceTypes.faq: INCIDENT_FAQ_DOCUMENT_DESCRIPTION,
    DocumentResourceTypes.case: CASE_INVESTIGATION_DOCUMENT_DESCRIPTION,
    DocumentResourceTypes.executive: INCIDENT_EXECUTIVE_REPORT_DOCUMENT_DESCRIPTION,
    DocumentResourceTypes.incident: INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION,
    DocumentResourceTypes.review: INCIDENT_REVIEW_DOCUMENT_DESCRIPTION,
    DocumentResourceTypes.tracking: INCIDENT_INVESTIGATION_SHEET_DESCRIPTION,
}

INCIDENT_RESOLUTION_DEFAULT = """
Description of the actions taken to resolve the incident.
""".replace("\n", " ").strip()

CASE_RESOLUTION_DEFAULT = """
Description of the actions taken to resolve the case.
""".replace("\n", " ").strip()

INCIDENT_COMPLETED_FORM_DESCRIPTION = """
A new {{form_type}} form related to incident {{name}} has been
submitted that requires your immediate attention. This form details
aspects related to potential legal implications. You can review the
detailed report by clicking on the link below. Please note, the information
contained in this report is confidential.
""".replace("\n", " ").strip()

INCIDENT_PARTICIPANT_WELCOME_DESCRIPTION = """
You\'ve been added to this incident, because we think you may
be able to help resolve it. Please review the incident details below and
reach out to the incident commander if you have any questions.""".replace("\n", " ").strip()

INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION = """
Dispatch thinks the following documents might be
relevant to this incident.""".replace("\n", " ").strip()

NOTIFICATION_PURPOSES_FYI = """
This message is for notification purposes only.""".replace("\n", " ").strip()

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

INCIDENT_REPORT_REMINDER_DELAYED_DESCRIPTION = """You asked me to send you this reminder to write a {{report_type}} for this incident.
You can use `{{command}}` in the conversation to assist you in writing one.""".replace(
    "\n", " "
).strip()

INCIDENT_CLOSE_REMINDER_DESCRIPTION = """The status of this incident hasn't been updated recently.
You can use `{{command}}` in the <{{conversation_weblink}}|conversation> to close the incident if it has been resolved and can be closed.""".replace(
    "\n", " "
).strip()

CASE_TRIAGE_REMINDER_DESCRIPTION = """The status of this case hasn't been updated recently.
Please ensure you triage the case based on its priority.""".replace("\n", " ").strip()

CASE_CLOSE_REMINDER_DESCRIPTION = """The status of this case hasn't been updated recently.
You can use the case 'Resolve' button if it has been resolved and can be closed.""".replace(
    "\n", " "
).strip()

INCIDENT_TASK_NEW_DESCRIPTION = """
The following incident task has been created and assigned to you by {{task_creator}}: {{task_description}}"""

INCIDENT_TASK_RESOLVED_DESCRIPTION = """
The following incident task has been resolved: {{task_description}}"""

INCIDENT_TASK_REMINDER_DESCRIPTION = """
The following incident tasks are assigned to you.
This is a reminder that these tasks have passed their due date.
Please review and mark them as resolved if appropriate. Resolving them will stop the reminders.""".replace(
    "\n", " "
).strip()

INCIDENT_TASK_LIST_DESCRIPTION = """The following are open incident tasks."""

INCIDENT_OPEN_TASKS_DESCRIPTION = """
Please resolve or transfer ownership of all the open incident tasks assigned to you in the incident documents or using the <{{dispatch_ui_url}}|Dispatch Web UI>,
then wait about 30 seconds for Dispatch to update the tasks before leaving the incident conversation.
""".replace("\n", " ").strip()

INCIDENT_TASK_ADD_TO_INCIDENT_DESCRIPTION = """
You have been added to this incident because you were assigned a task related to it. View all tasks for this incident using the <{{dispatch_ui_url}}|Dispatch Web UI>
\n\n *Task Description:* {{task_description}}
\n\n *Link to task in document:* {{task_weblink}}
"""

INCIDENT_MONITOR_CREATED_DESCRIPTION = """
A new monitor instance has been created.
\n\n *Weblink:* {{weblink}}
"""

INCIDENT_MONITOR_UPDATE_DESCRIPTION = """
This monitor detected a change in state. State has changed from *{{ monitor_state_old }}* to *{{ monitor_state_new }}*.
"""

INCIDENT_MONITOR_IGNORED_DESCRIPTION = """
This monitor is now ignored. Dispatch won't remind this incident channel about it again.
\n\n *Weblink:* {{weblink}}
"""

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
Thanks for closing incident {{name}}. Please, take a minute to review and update the following incident information in the <{{dispatch_ui_incident_url}}|Dispatch Web UI>:
\n • Incident Title: {{title}}
\n • Incident Description: {{description}}
\n • Incident Resolution: {{resolution}}
\n • Incident Type: {{type}}
\n • Incident Severity: {{severity}}
\n • Incident Priority: {{priority}}
\n Also, please consider taking the following actions:
\n • Update or add any relevant tags to the incident using the <{{dispatch_ui_incident_url}}|Dispatch Web UI>.
\n • Add any relevant, non-operational costs to the incident using the <{{dispatch_ui_incident_url}}|Dispatch Web UI>.
\n • Review and close any incident tasks that are no longer relevant or required.
"""

INCIDENT_CLOSED_RATING_FEEDBACK_DESCRIPTION = """
Thanks for participating in the {{name}} ("{{title}}") incident. We would appreciate if you could rate your experience and provide feedback."""

INCIDENT_MANAGEMENT_HELP_TIPS_MESSAGE_DESCRIPTION = """
Hey, I see you're the Incident Commander for <{{conversation_weblink}}|{{name}}> ("{{title}}"). Here are a few things to consider when managing the incident:
\n • Keep the incident and its status up to date using the Slack `{{update_command}}` command.
\n • Invite incident participants and team oncalls by mentioning them in the incident channel or using the Slack `{{engage_oncall_command}}` command.
\n • Keep incident participants and stakeholders informed by creating tactical and executive reports using the `{{tactical_report_command}}` and `{{executive_report_command}}` commands.
\n • Get links to incident resources from the <{{dispatch_ui_incident_url}}|Dispatch Web UI> or bookmarks in the incident conversation.
\n
To find a Slack command, simply type `/` in the message field or click the lightning bolt icon to the left of the message field.
"""

ONCALL_SHIFT_FEEDBACK_DESCRIPTION = """
Hi {{ individual_name }}, it appears that your {{ oncall_service_name }} shift recently completed on {{ shift_end_at }} UTC. To help us understand the impact on our responders, we would appreciate your feedback."""

ONCALL_SHIFT_FEEDBACK_RECEIVED_DESCRIPTION = """
We received your feedback for your shift that ended {{ shift_end_at }} UTC. Thank you!"""

INCIDENT_STATUS_CHANGE_DESCRIPTION = """
The incident status has been changed from {{ incident_status_old }} to {{ incident_status_new }}.""".replace(
    "\n", " "
).strip()

INCIDENT_TYPE_CHANGE_DESCRIPTION = """
The incident type has been changed from {{ incident_type_old }} to {{ incident_type_new }}.""".replace(
    "\n", " "
).strip()

INCIDENT_SEVERITY_CHANGE_DESCRIPTION = """
The incident severity has been changed from {{ incident_severity_old }} to {{ incident_severity_new }}.""".replace(
    "\n", " "
).strip()

INCIDENT_PRIORITY_CHANGE_DESCRIPTION = """
The incident priority has been changed from {{ incident_priority_old }} to {{ incident_priority_new }}.""".replace(
    "\n", " "
).strip()

INCIDENT_NAME_WITH_ENGAGEMENT = {
    "title": "{{name}} Incident Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
    "buttons": [
        {
            "button_text": "Subscribe",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.subscribe_user,
        },
        {
            "button_text": "Join",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.invite_user,
        },
    ],
}

INCIDENT_NAME_WITH_ENGAGEMENT_NO_DESCRIPTION = {
    "title": "{{name}}",
    "title_link": "{{ticket_weblink}}",
    "text": "{{ignore}}",
    "buttons": [
        {
            "button_text": "Subscribe",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.subscribe_user,
        },
        {
            "button_text": "Join",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.invite_user,
        },
    ],
}

INCIDENT_NAME_WITH_ENGAGEMENT_NO_SELF_JOIN = {
    "title": "{{name}} Incident Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
    "buttons": [
        {
            "button_text": "Subscribe",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.subscribe_user,
        },
    ],
}

CASE_NAME = {
    "title": "{{name}} Case Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
}

CASE_NAME_WITH_ENGAGEMENT = {
    "title": "{{name}} Case Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
    "buttons": [
        {
            "button_text": "Join",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.invite_user,
        },
    ],
}

CASE_NAME_WITH_ENGAGEMENT_NO_DESCRIPTION = {
    "title": "{{name}}",
    "title_link": "{{ticket_weblink}}",
    "text": "{{ignore}}",
    "buttons": [
        {
            "button_text": "Join",
            "button_value": "{{organization_slug}}-{{incident_id}}",
            "button_action": ConversationButtonActions.invite_user,
        },
    ],
}

CASE_NAME_WITH_ENGAGEMENT_NO_SELF_JOIN = {
    "title": "{{name}} Case Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
}

CASE_STATUS_CHANGE_DESCRIPTION = """
The case status has been changed from {{ case_status_old }} to {{ case_status_new }}.""".replace(
    "\n", " "
).strip()

CASE_TYPE_CHANGE_DESCRIPTION = """
The case type has been changed from {{ case_type_old }} to {{ case_type_new }}.""".replace(
    "\n", " "
).strip()

CASE_SEVERITY_CHANGE_DESCRIPTION = """
The case severity has been changed from {{ case_severity_old }} to {{ case_severity_new }}.""".replace(
    "\n", " "
).strip()

CASE_PRIORITY_CHANGE_DESCRIPTION = """
The case priority has been changed from {{ case_priority_old }} to {{ case_priority_new }}.""".replace(
    "\n", " "
).strip()

CASE_STATUS_CHANGE = {
    "title": "Status Change",
    "text": CASE_STATUS_CHANGE_DESCRIPTION,
}

CASE_TYPE_CHANGE = {"title": "Case Type Change", "text": CASE_TYPE_CHANGE_DESCRIPTION}

CASE_SEVERITY_CHANGE = {
    "title": "Severity Change",
    "text": CASE_SEVERITY_CHANGE_DESCRIPTION,
}

CASE_PRIORITY_CHANGE = {
    "title": "Priority Change",
    "text": CASE_PRIORITY_CHANGE_DESCRIPTION,
}

INCIDENT_NAME = {
    "title": "{{name}} Incident Notification",
    "title_link": "{{ticket_weblink}}",
    "text": NOTIFICATION_PURPOSES_FYI,
}

INCIDENT_TITLE = {"title": "Title", "text": "{{title}}"}

CASE_TITLE = {"title": "Title", "text": "{{title}}"}

CASE_STATUS = {
    "title": "Status - {{status}}",
    "status_mapping": CASE_STATUS_DESCRIPTIONS,
}

FORM_TYPE_DESCRIPTION = {
    "title": "{{form_type}} form for incident {{name}}",
    "title_link": "{{form_weblink}}",
    "text": "{{form_type_description}}",
}

INCIDENT_DATA_SECTION = {
    "type": "context",
    "text": "Key details about incident {{name}}",
}

if config.DISPATCH_MARKDOWN_IN_INCIDENT_DESC:
    INCIDENT_DESCRIPTION = {"title": "Description", "text": "{{description | markdown}}"}
else:
    INCIDENT_DESCRIPTION = {"title": "Description", "text": "{{description}}"}

INCIDENT_STATUS = {
    "title": "Status - {{status}}",
    "status_mapping": INCIDENT_STATUS_DESCRIPTIONS,
}

INCIDENT_VISIBILITY = {
    "title": "Visibility - {{visibility}}",
    "visibility_mapping": INCIDENT_VISIBILITY_DESCRIPTIONS,
}

INCIDENT_TYPE = {"title": "Type - {{type}}", "text": "{{type_description}}"}

INCIDENT_SEVERITY = {
    "title": "Severity - {{severity}}",
    "text": "{{severity_description}}",
}

INCIDENT_SEVERITY_FYI = {
    "title": "Severity - {{severity}}",
    "text": "{{severity_description}}",
}
INCIDENT_PRIORITY = {
    "title": "Priority - {{priority}}",
    "text": "{{priority_description}}",
}

INCIDENT_PRIORITY_FYI = {
    "title": "Priority - {{priority}}",
    "text": "{{priority_description}}",
}

INCIDENT_REPORTER = {
    "title": "Reporter - {{reporter_fullname}}, {{reporter_team}}",
    "title_link": "{{reporter_weblink}}",
    "text": INCIDENT_REPORTER_DESCRIPTION,
}

INCIDENT_COMMANDER = {
    "title": "Commander - {{commander_fullname}}, {{commander_team}}",
    "title_link": "{{commander_weblink}}",
    "text": INCIDENT_COMMANDER_DESCRIPTION,
}

INCIDENT_CONFERENCE = {
    "title": "Conference",
    "title_link": "{{conference_weblink}}",
    "text": INCIDENT_CONFERENCE_DESCRIPTION,
}

INCIDENT_STORAGE = {
    "title": "Storage",
    "title_link": "{{storage_weblink}}",
    "text": STORAGE_DESCRIPTION,
}

INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT = {
    "title": "Incident Conversation Commands Reference Document",
    "title_link": "{{conversation_commands_reference_document_weblink}}",
    "text": INCIDENT_CONVERSATION_REFERENCE_DOCUMENT_DESCRIPTION,
}

INCIDENT_INVESTIGATION_DOCUMENT = {
    "title": "Investigation Document",
    "title_link": "{{document_weblink}}",
    "text": INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION,
}

INCIDENT_REVIEW_DOCUMENT = {
    "title": "Review Document",
    "title_link": "{{review_document_weblink}}",
    "text": INCIDENT_REVIEW_DOCUMENT_DESCRIPTION,
}

INCIDENT_FAQ_DOCUMENT = {
    "title": "FAQ Document",
    "title_link": "{{faq_weblink}}",
    "text": INCIDENT_FAQ_DOCUMENT_DESCRIPTION,
}

INCIDENT_STATUS_CHANGE = {
    "title": "Status Change",
    "text": INCIDENT_STATUS_CHANGE_DESCRIPTION,
}

INCIDENT_TYPE_CHANGE = {"title": "Incident Type Change", "text": INCIDENT_TYPE_CHANGE_DESCRIPTION}

INCIDENT_SEVERITY_CHANGE = {
    "title": "Severity Change",
    "text": INCIDENT_SEVERITY_CHANGE_DESCRIPTION,
}

INCIDENT_PRIORITY_CHANGE = {
    "title": "Priority Change",
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

INCIDENT_COMPLETED_FORM = {
    "title": "Completed {{form_type}} form notification for {{name}}",
    "text": INCIDENT_COMPLETED_FORM_DESCRIPTION,
}

INCIDENT_PARTICIPANT_WELCOME_MESSAGE = [
    INCIDENT_PARTICIPANT_WELCOME,
    INCIDENT_TITLE,
    INCIDENT_DESCRIPTION,
    INCIDENT_VISIBILITY,
    INCIDENT_STATUS,
    INCIDENT_TYPE,
    INCIDENT_SEVERITY,
    INCIDENT_PRIORITY,
    INCIDENT_REPORTER,
    INCIDENT_COMMANDER,
    INCIDENT_INVESTIGATION_DOCUMENT,
    INCIDENT_STORAGE,
    INCIDENT_CONFERENCE,
    INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
    INCIDENT_FAQ_DOCUMENT,
]

INCIDENT_COMPLETED_FORM_MESSAGE = [
    INCIDENT_COMPLETED_FORM,
    FORM_TYPE_DESCRIPTION,
    INCIDENT_DATA_SECTION,
    INCIDENT_TITLE,
    INCIDENT_DESCRIPTION,
    INCIDENT_STATUS,
    INCIDENT_COMMANDER,
]

INCIDENT_NOTIFICATION_COMMON = [INCIDENT_TITLE]

INCIDENT_NOTIFICATION = INCIDENT_NOTIFICATION_COMMON.copy()
INCIDENT_NOTIFICATION.extend(
    [
        INCIDENT_DESCRIPTION,
        INCIDENT_STATUS,
        INCIDENT_TYPE,
        INCIDENT_SEVERITY_FYI,
        INCIDENT_PRIORITY_FYI,
        INCIDENT_REPORTER,
        INCIDENT_COMMANDER,
    ]
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

REMIND_AGAIN_OPTIONS = {
    "text": "[Optional] Remind me again in:",
    "select": {
        "placeholder": "Choose a time value",
        "select_action": ConversationButtonActions.remind_again,
        "options": [
            {
                "option_text": value["message"],
                "option_value": "{{organization_slug}}-{{incident_id}}-{{report_type}}-" + key,
            }
            for key, value in reminder_select_values.items()
        ],
    },
}

INCIDENT_REPORT_REMINDER = [
    {
        "title": "{{name}} Incident - {{report_type}} Reminder",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_REPORT_REMINDER_DESCRIPTION,
    },
    INCIDENT_TITLE,
    REMIND_AGAIN_OPTIONS,
]

INCIDENT_REPORT_REMINDER_DELAYED = [
    {
        "title": "{{name}} Incident - {{report_type}} Reminder",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_REPORT_REMINDER_DELAYED_DESCRIPTION,
    },
    INCIDENT_TITLE,
    REMIND_AGAIN_OPTIONS,
]


INCIDENT_CLOSE_REMINDER = [
    {
        "title": "{{name}} Incident - Close Reminder",
        "title_link": "{{dispatch_ui_incident_url}}",
        "text": INCIDENT_CLOSE_REMINDER_DESCRIPTION,
    },
    INCIDENT_TITLE,
    INCIDENT_STATUS,
]


CASE_CLOSE_REMINDER = [
    {
        "title": "{{name}} Case - Close Reminder",
        "title_link": "{{dispatch_ui_case_url}}",
        "text": CASE_CLOSE_REMINDER_DESCRIPTION,
    },
    CASE_TITLE,
    CASE_STATUS,
]

CASE_TRIAGE_REMINDER = [
    {
        "title": "{{name}} Case - Triage Reminder",
        "title_link": "{{dispatch_ui_case_url}}",
        "text": CASE_TRIAGE_REMINDER_DESCRIPTION,
    },
    CASE_TITLE,
    CASE_STATUS,
]

CASE_ASSIGNEE_DESCRIPTION = """
The Case Assignee is responsible for
knowing the full context of the case.
Contact them about any questions or concerns.""".replace("\n", " ").strip()

CASE_REPORTER_DESCRIPTION = """
The person who reported the case. Contact them if the report details need clarification.""".replace(
    "\n", " "
).strip()

CASE_REPORTER = {
    "title": "Reporter - {{reporter_fullname}}, {{reporter_team}}",
    "title_link": "{{reporter_weblink}}",
    "text": CASE_REPORTER_DESCRIPTION,
}

CASE_ASSIGNEE = {
    "title": "Assignee - {{assignee_fullname}}, {{assignee_team}}",
    "title_link": "{{assignee_weblink}}",
    "text": CASE_ASSIGNEE_DESCRIPTION,
}

CASE_NOTIFICATION_COMMON = [CASE_TITLE]

CASE_NOTIFICATION = CASE_NOTIFICATION_COMMON.copy()
CASE_NOTIFICATION.extend(
    [
        INCIDENT_DESCRIPTION,
        CASE_STATUS,
        INCIDENT_TYPE,
        INCIDENT_SEVERITY_FYI,
        INCIDENT_PRIORITY_FYI,
        CASE_REPORTER,
        CASE_ASSIGNEE,
    ]
)


INCIDENT_TASK_REMINDER = [
    {"title": "Incident - {{ name }}", "text": "{{ title }}"},
    {"title": "Creator", "text": "{{ creator }}"},
    {"title": "Description", "text": "{{ description }}"},
    {"title": "Priority", "text": "{{ priority }}"},
    {"title": "Created At", "text": "", "datetime": "{{ created_at}}"},
    {"title": "Resolve By", "text": "", "datetime": "{{ resolve_by }}"},
    {"title": "Link", "text": "{{ weblink }}"},
]

EVERGREEN_REMINDER = [
    {"title": "Project", "text": "{{ project }}"},
    {"title": "Type", "text": "{{ resource_type }}"},
    {"title": "Name", "text": "{{ name }}"},
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

INCIDENT_MONITOR_CREATED_NOTIFICATION = [
    {
        "title": "Monitor Created",
        "title_link": "{{weblink}}",
        "text": INCIDENT_MONITOR_CREATED_DESCRIPTION,
    }
]

INCIDENT_MONITOR_UPDATE_NOTIFICATION = [
    {
        "title": "Monitor Status Change",
        "title_link": "{{weblink}}",
        "text": INCIDENT_MONITOR_UPDATE_DESCRIPTION,
    }
]

INCIDENT_MONITOR_IGNORE_NOTIFICATION = [
    {
        "title": "Monitor Ignored",
        "title_link": "{{weblink}}",
        "text": INCIDENT_MONITOR_IGNORED_DESCRIPTION,
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
        "title_link": "{{dispatch_ui_incident_url}}",
        "text": INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_DESCRIPTION,
    }
]

INCIDENT_CLOSED_RATING_FEEDBACK_NOTIFICATION = [
    {
        "title": "{{name}} Incident - Rating and Feedback",
        "title_link": "{{ticket_weblink}}",
        "text": INCIDENT_CLOSED_RATING_FEEDBACK_DESCRIPTION,
        "buttons": [
            {
                "button_text": "Provide Feedback",
                "button_value": "{{organization_slug}}-{{incident_id}}",
                "button_action": ConversationButtonActions.feedback_notification_provide,
            }
        ],
    }
]

INCIDENT_FEEDBACK_DAILY_REPORT = [
    {"title": "Incident", "text": "{{ name }}"},
    {"title": "Incident Title", "text": "{{ title }}"},
    {"title": "Rating", "text": "{{ rating }}"},
    {"title": "Feedback", "text": "{{ feedback }}"},
    {"title": "Participant", "text": "{{ participant }}"},
    {"title": "Created At", "text": "", "datetime": "{{ created_at}}"},
]

INCIDENT_DAILY_REPORT_HEADER = {
    "type": "header",
    "text": INCIDENT_DAILY_REPORT_TITLE,
}

INCIDENT_DAILY_REPORT_HEADER_DESCRIPTION = {
    "text": INCIDENT_DAILY_REPORT_DESCRIPTION,
}

INCIDENT_DAILY_REPORT_FOOTER = {
    "type": "context",
    "text": INCIDENT_DAILY_REPORT_FOOTER_CONTEXT,
}

INCIDENT_DAILY_REPORT = [
    INCIDENT_DAILY_REPORT_HEADER,
    INCIDENT_DAILY_REPORT_HEADER_DESCRIPTION,
    INCIDENT_DAILY_REPORT_FOOTER,
]

INCIDENT = [
    INCIDENT_NAME_WITH_ENGAGEMENT_NO_DESCRIPTION,
    INCIDENT_TITLE,
    INCIDENT_STATUS,
    INCIDENT_TYPE,
    INCIDENT_SEVERITY,
    INCIDENT_PRIORITY,
    INCIDENT_COMMANDER,
]


INCIDENT_MANAGEMENT_HELP_TIPS_MESSAGE = [
    {
        "title": "{{name}} Incident - Management Help Tips",
        "text": INCIDENT_MANAGEMENT_HELP_TIPS_MESSAGE_DESCRIPTION,
    }
]

INCIDENT_OPEN_TASKS = [
    {
        "title": "{{title}}",
        "text": INCIDENT_OPEN_TASKS_DESCRIPTION,
    }
]

INCIDENT_TASK_ADD_TO_INCIDENT = [
    {
        "title": "{{title}}",
        "text": INCIDENT_TASK_ADD_TO_INCIDENT_DESCRIPTION,
    }
]

ONCALL_SHIFT_FEEDBACK_BUTTONS = [
    {
        "button_text": "Provide Feedback",
        "button_value": "{{organization_slug}}|{{project_id}}|{{oncall_schedule_id}}|{{shift_end_at}}|{{reminder_id}}",
        "button_action": ConversationButtonActions.service_feedback,
    }
]

ONCALL_SHIFT_FEEDBACK_NOTIFICATION = [
    {
        "title": "Oncall Shift Feedback",
        "text": ONCALL_SHIFT_FEEDBACK_DESCRIPTION,
        "buttons": ONCALL_SHIFT_FEEDBACK_BUTTONS,
    }
]

ONCALL_SHIFT_FEEDBACK_NOTIFICATION_REMINDER = [
    {
        "title": "Oncall Shift Feedback - REMINDER",
        "text": ONCALL_SHIFT_FEEDBACK_DESCRIPTION,
        "buttons": ONCALL_SHIFT_FEEDBACK_BUTTONS,
    }
]

ONCALL_SHIFT_FEEDBACK_RECEIVED = [
    {
        "title": "Oncall Shift Feedback - RECEIVED",
        "text": ONCALL_SHIFT_FEEDBACK_RECEIVED_DESCRIPTION,
    }
]


def render_message_template(message_template: List[dict], **kwargs):
    """Renders the jinja data included in the template itself."""
    data = []
    new_copy = copy.deepcopy(message_template)
    for d in new_copy:
        if d.get("header"):
            d["header"] = env.from_string(d["header"]).render(**kwargs)

        if d.get("title"):
            d["title"] = env.from_string(d["title"]).render(**kwargs)

        if d.get("title_link"):
            d["title_link"] = env.from_string(d["title_link"]).render(**kwargs)

            if d["title_link"] == "None":  # skip blocks with no content
                continue

            # skip blocks that do not have new links rendered, as no real value was provided
            if not d["title_link"]:
                continue

        if d.get("text"):
            d["text"] = env.from_string(d["text"]).render(**kwargs)

            # NOTE: we truncate the string to 2500 characters
            # to prevent hitting limits on SaaS integrations (e.g. Slack)
            d["text"] = d["text"] if len(d["text"]) <= 2500 else d["text"][:2500]

        # render a new button array given the template
        if d.get("buttons"):
            for button in d["buttons"]:
                button["button_text"] = env.from_string(button["button_text"]).render(**kwargs)
                button["button_value"] = env.from_string(button["button_value"]).render(**kwargs)

                if button.get("button_action"):
                    button["button_action"] = env.from_string(button["button_action"]).render(
                        **kwargs
                    )

                if button.get("button_url"):
                    button["button_url"] = env.from_string(button["button_url"]).render(**kwargs)

        # render drop-down list
        if select := d.get("select"):
            if placeholder := select.get("placeholder"):
                select["placeholder"] = env.from_string(placeholder).render(**kwargs)

            select["select_action"] = env.from_string(select["select_action"]).render(**kwargs)

            for option in select["options"]:
                option["option_text"] = env.from_string(option["option_text"]).render(**kwargs)
                option["option_value"] = env.from_string(option["option_value"]).render(**kwargs)

        if d.get("visibility_mapping"):
            d["text"] = d["visibility_mapping"][kwargs["visibility"]]

        if d.get("status_mapping"):
            d["text"] = d["status_mapping"][kwargs["status"]]

        if d.get("datetime"):
            d["datetime"] = env.from_string(d["datetime"]).render(**kwargs)

        if d.get("context"):
            d["context"] = env.from_string(d["context"]).render(**kwargs)

        data.append(d)

    return data


def generate_welcome_message(welcome_message: EmailTemplates) -> Optional[List[dict]]:
    """Generates the welcome message."""
    if welcome_message is None:
        return INCIDENT_PARTICIPANT_WELCOME_MESSAGE

    participant_welcome = {
        "title": welcome_message.welcome_text,
        "title_link": "{{ticket_weblink}}",
        "text": welcome_message.welcome_body,
    }

    component_mapping = {
        "Title": INCIDENT_TITLE,
        "Description": INCIDENT_DESCRIPTION,
        "Visibility": INCIDENT_VISIBILITY,
        "Status": INCIDENT_STATUS,
        "Type": INCIDENT_TYPE,
        "Severity": INCIDENT_SEVERITY,
        "Priority": INCIDENT_PRIORITY,
        "Reporter": INCIDENT_REPORTER,
        "Commander": INCIDENT_COMMANDER,
        "Investigation Document": INCIDENT_INVESTIGATION_DOCUMENT,
        "Storage": INCIDENT_STORAGE,
        "Conference": INCIDENT_CONFERENCE,
        "Slack Commands": INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
        "FAQ Document": INCIDENT_FAQ_DOCUMENT,
    }

    message = [participant_welcome]

    for component in component_mapping.keys():
        # if the component type is in welcome_message.components, then add it
        if component in welcome_message.components:
            message.append(component_mapping[component])

    return message
