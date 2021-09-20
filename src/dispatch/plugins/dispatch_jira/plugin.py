"""
.. module: dispatch.plugins.dispatch_jira.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from enum import Enum
from typing import Any

from pydantic import Field, SecretStr, HttpUrl

from jinja2 import Template
from jira import JIRA, User

from dispatch.config import BaseConfigurationModel
from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_jira as jira_plugin
from dispatch.plugins.bases import TicketPlugin


class HostingType(str, Enum):
    """Type of Jira deployment."""

    cloud = "cloud"
    server = "server"


class JiraConfiguration(BaseConfigurationModel):
    """Jira configuration description."""

    api_url: HttpUrl = Field(
        title="API URL", description="This URL is used for communication with API."
    )
    browser_url: HttpUrl = Field(
        title="Browser URL", description="This URL is used to construct browser weblinks."
    )
    hosting_type: HostingType = Field(
        "cloud", title="Hosting Type", description="Defines the type of deployment."
    )
    username: str = Field(
        title="Username", description="Username to use to authenticate to Jira API."
    )
    password: SecretStr = Field(
        title="Password", description="Password to use to authenticate to Jira API."
    )


ISSUE_SUMMARY_TEMPLATE = """
{color:red}*Confidential Information - For Internal Use Only*{color}

*Incident Details*
Description: {{description}}
Type: {{incident_type}}
Priority: {{priority}}
Cost: {{cost}}

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


def get_user_field(client: JIRA, hosting_type: str, jira_username: str, user_email: str) -> dict:
    """Returns correct Jira user field based on Jira hosting type."""
    if hosting_type == "server":
        username = get_email_username(user_email)
        users = client.search_users(user=username)
        for user in users:
            if user.name == username:
                return {"name": user.name}

        # we default to the Jira user we use for managing issues
        # if we can't find the user in Jira
        return {"name": jira_username}
    if hosting_type == "sloud":
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
    """Processes the given incident type plugin metadata."""
    project_id = None
    issue_type_name = None
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
    cost = f"${cost:,.2f}"

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


def create(configuration: dict, client: Any, issue_fields: dict) -> dict:
    """Creates a Jira issue."""
    issue = client.create_issue(fields=issue_fields)
    return {"resource_id": issue.key, "weblink": f"{configuration.browser_url}/browse/{issue.key}"}


def update(
    configuration: dict, client: Any, issue: Any, issue_fields: dict, transition: str = None
) -> dict:
    """Updates a Jira issue."""
    data = {"resource_id": issue.key, "link": f"{configuration.browser_url}/browse/{issue.key}"}

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

    def __init__(self):
        self.configuration_schema = JiraConfiguration

    def create(
        self,
        incident_id: int,
        title: str,
        incident_type: str,
        incident_priority: str,
        commander_email: str,
        reporter_email: str,
        incident_type_plugin_metadata: dict = {},
        db_session=None,
    ):
        """Creates a Jira issue."""
        client = JIRA(
            self.configuration.api_url,
            basic_auth=(
                self.configuration.username,
                self.configuration.password.get_secret_value(),
            ),
        )

        assignee = get_user_field(
            client, self.configuration.hosting_type, self.configuration.username, commander_email
        )
        reporter = get_user_field(
            client, self.configuration.hosting_type, self.configuration.username, reporter_email
        )

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

        return create(self.configuration, client, issue_fields)

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
        client = JIRA(
            self.configuration.api_url,
            basic_auth=(
                self.configuration.username,
                self.configuration.password.get_secret_value(),
            ),
        )

        assignee = get_user_field(
            client, self.configuration.hosting_type, self.configuration.username, commander_email
        )
        reporter = get_user_field(
            client, self.configuration.hosting_type, self.configuration.username, reporter_email
        )

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

        return update(self.configuration, client, issue, issue_fields, status)
