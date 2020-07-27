"""
.. module: dispatch.plugins.dispatch_jira.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from jinja2 import Template
from jira import JIRA
from typing import Any

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_jira as jira_plugin
from dispatch.plugins.bases import TicketPlugin

from .config import (
    JIRA_BROWSER_URL,
    JIRA_API_URL,
    JIRA_USERNAME,
    JIRA_PASSWORD,
    JIRA_PROJECT_KEY,
    JIRA_ISSUE_TYPE_ID,
)


ISSUE_SUMMARY_TEMPLATE = """
{color:red}*Confidential Information - For Internal Use Only*{color}

*Incident Details*
Description: {{description}}
Type: {{incident_type}}
Priority: {{priority}}
Cost: ${{cost}}

*Incident Resources*
[Conversation|{{conversation_weblink}}]
[Investigation Document|{{document_weblink}}]
[Storage|{{storage_weblink}}]
[Conference|{{conference_weblink}}]

Incident Commander: [~{{commander_username}}]
"""


def create_issue_fields(
    title: str,
    description: str,
    incident_type: str,
    priority: str,
    commander_username: str,
    reporter_username: str,
    conversation_weblink: str,
    document_weblink: str,
    storage_weblink: str,
    conference_weblink: str,
    cost: float,
):
    """Creates Jira issue fields."""
    issue_fields = {}

    issue_fields.update({"summary": title})
    issue_fields.update({"assignee": {"name": commander_username}})
    issue_fields.update({"reporter": {"name": reporter_username}})

    description = Template(ISSUE_SUMMARY_TEMPLATE).render(
        description=description,
        incident_type=incident_type,
        priority=priority,
        cost=cost,
        commander_username=commander_username,
        document_weblink=document_weblink,
        conference_weblink=conference_weblink,
        conversation_weblink=conversation_weblink,
        storage_weblink=storage_weblink,
    )
    issue_fields.update({"description": description})

    return issue_fields


def create(client: Any, issue_fields: dict, type: str = JIRA_PROJECT_KEY) -> dict:
    """Creates a Jira issue."""
    issue = client.create_issue(fields=issue_fields)
    return {"resource_id": issue.key, "weblink": f"{JIRA_BROWSER_URL}/browse/{issue.key}"}


def update(client: Any, issue: Any, issue_fields: dict, transition: str = None) -> dict:
    """Updates a Jira issue."""
    data = {"resource_id": issue.key, "link": f"{JIRA_BROWSER_URL}/browse/{issue.key}"}

    if issue_fields:
        issue.update(fields=issue_fields)

    if transition:
        transitions = client.transitions(issue)
        for t in transitions:
            if t["name"].lower() == transition.lower():
                client.transition_issue(issue, t["id"])
                break

    return data


def get_user_name(email):
    """Returns username part of email, if valid email is provided."""
    if "@" in email:
        return email.split("@")[0]
    return email


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class JiraTicketPlugin(TicketPlugin):
    title = "Jira Plugin - Ticket Management"
    slug = "jira-ticket"
    description = "Uses Jira to help manage external tickets."
    version = jira_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    _schema = None

    def create(
        self,
        incident_id: int,
        title: str,
        incident_type: str,
        incident_priority: str,
        commander: str,
        reporter: str,
        incident_type_plugin_metadata: dict = {},
    ):
        """Creates a Jira issue."""
        client = JIRA(str(JIRA_API_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))

        commander_username = get_user_name(commander)
        reporter_username = get_user_name(reporter)

        issue_fields = {
            "project": {"key": JIRA_PROJECT_KEY},
            "issuetype": {"id": JIRA_ISSUE_TYPE_ID},
            "summary": title,
            "assignee": {"name": commander_username},
            "reporter": {"name": reporter_username},
        }

        return create(client, issue_fields, type=JIRA_PROJECT_KEY)

    def update(
        self,
        ticket_id: str,
        title: str,
        description: str,
        incident_type: str,
        priority: str,
        status: str,
        commander_email: str,
        reporter_email: str,
        conversation_weblink: str,
        document_weblink: str,
        storage_weblink: str,
        conference_weblink: str,
        cost: float,
        incident_type_plugin_metadata: dict = {},
    ):
        """Updates Jira issue fields."""
        client = JIRA(str(JIRA_API_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))

        commander_username = get_user_name(commander_email)
        reporter_username = get_user_name(reporter_email)

        issue = client.issue(ticket_id)
        issue_fields = create_issue_fields(
            title=title,
            description=description,
            incident_type=incident_type,
            priority=priority,
            commander_username=commander_username,
            reporter_username=reporter_username,
            conversation_weblink=conversation_weblink,
            document_weblink=document_weblink,
            storage_weblink=storage_weblink,
            conference_weblink=conference_weblink,
            cost=cost,
        )

        return update(client, issue, issue_fields, status)
