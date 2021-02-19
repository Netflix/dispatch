"""
.. module: dispatch.plugins.dispatch_jira.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from typing import Any

from jinja2 import Template
from jira import JIRA, User

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_jira as jira_plugin
from dispatch.plugins.bases import TicketPlugin

from .config import (
    JIRA_API_URL,
    JIRA_BROWSER_URL,
    JIRA_HOSTING_TYPE,
    JIRA_ISSUE_TYPE_NAME,
    JIRA_PASSWORD,
    JIRA_PROJECT_ID,
    JIRA_USERNAME,
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


def get_email_username(email: str) -> str:
    """Returns username part of email, if valid email is provided."""
    if "@" in email:
        return email.split("@")[0]
    return email


def get_user_field(client: JIRA, user_email) -> dict:
    """Returns correct Jira user field based on Jira hosting option."""
    if JIRA_HOSTING_TYPE == "Server":
        user = client.search_users(user_email, maxResults=1)[0]
        return {"name": user.name}
    if JIRA_HOSTING_TYPE == "Cloud":
        username = get_email_username(user_email)
        user = next(
            client._fetch_pages(
                User,
                None,
                "user/search",
                startAt=0,
                maxResults=1,
                params={"query": username},
            )
        )
        return {"id": user.accountId}


def process_incident_type_plugin_metadata(plugin_metadata: dict):
    """
    Processes the given incident type plugin metadata.
    """
    project_id = JIRA_PROJECT_ID
    issue_type_name = JIRA_ISSUE_TYPE_NAME
    if plugin_metadata:
        for key_value in plugin_metadata["metadata"]:
            if key_value["key"] == "project_id":
                project_id = key_value["value"]
            if key_value["key"] == "issue_type_name":
                issue_type_name = key_value["value"]

    return project_id, issue_type_name


def create_issue_fields(
    title: str,
    description: str,
    incident_type: str,
    priority: str,
    assignee: dict,
    reporter: dict,
    commander_username: str,
    conversation_weblink: str,
    document_weblink: str,
    storage_weblink: str,
    conference_weblink: str,
    cost: float,
):
    """Creates Jira issue fields."""
    issue_fields = {}

    issue_fields.update({"summary": title})
    issue_fields.update({"assignee": assignee})
    issue_fields.update({"reporter": reporter})

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


def create(client: Any, issue_fields: dict) -> dict:
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
        commander_email: str,
        reporter_email: str,
        incident_type_plugin_metadata: dict = {},
    ):
        """Creates a Jira issue."""
        client = JIRA(str(JIRA_API_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))

        assignee = get_user_field(client, commander_email)
        reporter = get_user_field(client, reporter_email)

        project_id, issue_type_name = process_incident_type_plugin_metadata(
            incident_type_plugin_metadata
        )

        issue_fields = {
            "project": {"id": project_id},
            "issuetype": {"name": issue_type_name},
            "assignee": assignee,
            "reporter": reporter,
            "summary": title,
        }

        return create(client, issue_fields)

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

        assignee = get_user_field(client, commander_email)
        reporter = get_user_field(client, reporter_email)

        commander_username = get_email_username(commander_email)

        issue = client.issue(ticket_id)
        issue_fields = create_issue_fields(
            title=title,
            description=description,
            incident_type=incident_type,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            commander_username=commander_username,
            conversation_weblink=conversation_weblink,
            document_weblink=document_weblink,
            storage_weblink=storage_weblink,
            conference_weblink=conference_weblink,
            cost=cost,
        )

        return update(client, issue, issue_fields, status)
