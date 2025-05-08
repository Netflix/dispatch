"""
.. module: dispatch.plugins.dispatch_jira.plugin
:platform: Unix
:copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
:license: Apache, see LICENSE for more details.
"""

import json
import logging
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from pydantic import Field, SecretStr, AnyHttpUrl

from jinja2 import Template
from jira import JIRA

from dispatch.config import BaseConfigurationModel
from dispatch.decorators import apply, counter, timer
from dispatch.enums import DispatchEnum
from dispatch.plugins import dispatch_jira as jira_plugin
from dispatch.case import service as case_service
from dispatch.incident import service as incident_service
from dispatch.plugins.bases import TicketPlugin
from dispatch.project.models import Project

from .templates import (
    CASE_ISSUE_SUMMARY_TEMPLATE,
    INCIDENT_ISSUE_SUMMARY_NO_RESOURCES_TEMPLATE,
    INCIDENT_ISSUE_SUMMARY_TEMPLATE,
)

from dispatch.config import DISPATCH_UI_URL

log = logging.getLogger(__name__)


class HostingType(DispatchEnum):
    """Type of Jira deployment."""

    cloud = "cloud"
    server = "server"


class JiraConfiguration(BaseConfigurationModel):
    """Jira configuration description."""

    default_project_id: str = Field(
        title="Default Project Id or Key", description="Defines the default Jira Project to use."
    )
    default_issue_type_name: str = Field(
        title="Default Issue Type Name",
        description="Defines the default Jira issue type name to use.",
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
    api_url: AnyHttpUrl = Field(
        title="API URL", description="This URL is used for communication with API."
    )
    browser_url: AnyHttpUrl = Field(
        title="Browser URL", description="This URL is used to construct browser weblinks."
    )


def get_email_username(email: str) -> str:
    """Returns username part of email, if valid email is provided."""
    if "@" in email:
        return email.split("@")[0]
    return email


def get_cloud_user_account_id_by_email(configuration: JiraConfiguration, user_email: str) -> dict:
    """Gets the cloud Jira user account id by email address."""
    endpoint = "groupuserpicker"
    url = f"{configuration.api_url}/rest/api/2/{endpoint}?query={user_email}&maxResults=1"
    auth = (configuration.username, configuration.password.get_secret_value())

    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, auth=HTTPBasicAuth(*auth))

    users = json.loads(response.text)
    if users["users"]["users"]:
        return users["users"]["users"][0]["accountId"]

    # we get and return the account id of the default Jira account
    url = (
        f"{configuration.api_url}/rest/api/2/{endpoint}?query={configuration.username}&maxResults=1"
    )
    response = requests.request("GET", url, headers=headers, auth=HTTPBasicAuth(*auth))
    users = json.loads(response.text)
    return users["users"]["users"][0]["accountId"]


def get_user_field(client: JIRA, configuration: JiraConfiguration, user_email: str) -> dict:
    """Returns correct Jira user field based on Jira hosting type."""
    if configuration.hosting_type == HostingType.server:
        username = get_email_username(user_email)
        users = client.search_users(user=username)
        for user in users:
            if user.name == username:
                return {"name": user.name}

        # we default to the Jira user we use for managing issues
        # if we can't find the user in Jira
        return {"name": configuration.username}
    if configuration.hosting_type == HostingType.cloud:
        user_account_id = get_cloud_user_account_id_by_email(configuration, user_email)
        return {"id": user_account_id}


def process_plugin_metadata(plugin_metadata: dict):
    """Processes plugin metadata."""
    project_id = None
    issue_type_name = None
    if plugin_metadata:
        for key_value in plugin_metadata["metadata"]:
            if key_value["key"] == "project_id":
                project_id = key_value["value"]
            if key_value["key"] == "issue_type_name":
                issue_type_name = key_value["value"]

    return project_id, issue_type_name


def create_dict_from_plugin_metadata(plugin_metadata: dict):
    """Creates a dictionary from plugin metadata, excluding project_id and issue_type_name."""
    metadata_dict = {}
    if plugin_metadata:
        for key_value in plugin_metadata["metadata"]:
            if key_value["key"] != "project_id" and key_value["key"] != "issue_type_name":
                metadata_dict[key_value["key"]] = key_value["value"]

    return metadata_dict


def create_client(configuration: JiraConfiguration) -> JIRA:
    """Creates a Jira client."""
    return JIRA(
        configuration.api_url,
        basic_auth=(configuration.username, configuration.password.get_secret_value()),
    )


def create_incident_issue_fields(
    title: str,
    description: str,
    incident_type: str,
    incident_severity: str,
    incident_priority: str,
    assignee: dict,
    reporter: dict,
    commander_username: str,
    conversation_weblink: str,
    document_weblink: str,
    storage_weblink: str,
    conference_weblink: str,
    dispatch_weblink: str,
    cost: float,
):
    """Creates Jira issue fields."""
    cost = f"${cost:,.2f}"

    issue_fields = {}
    issue_fields.update({"summary": title})
    issue_fields.update({"assignee": assignee})
    issue_fields.update({"reporter": reporter})

    if (
        conversation_weblink is None
        and document_weblink is None
        and storage_weblink is None
        and conference_weblink is None
    ):
        # the incident was opened as closed and we didn't create resources
        description = Template(INCIDENT_ISSUE_SUMMARY_NO_RESOURCES_TEMPLATE).render(
            description=description,
            incident_type=incident_type,
            incident_severity=incident_severity,
            incident_priority=incident_priority,
            cost=cost,
            commander_username=commander_username,
        )
    else:
        description = Template(INCIDENT_ISSUE_SUMMARY_TEMPLATE).render(
            description=description,
            incident_type=incident_type,
            incident_severity=incident_severity,
            incident_priority=incident_priority,
            cost=cost,
            commander_username=commander_username,
            document_weblink=document_weblink,
            conference_weblink=conference_weblink,
            conversation_weblink=conversation_weblink,
            storage_weblink=storage_weblink,
            dispatch_weblink=dispatch_weblink,
        )
    issue_fields.update({"description": description})

    return issue_fields


def create_case_issue_fields(
    title: str,
    description: str,
    resolution: str,
    case_type: str,
    case_severity: str,
    case_priority: str,
    assignee: dict,
    reporter: dict,
    assignee_username: str,
    document_weblink: str,
    storage_weblink: str,
    dispatch_weblink: str,
):
    """Creates Jira issue fields."""
    issue_fields = {}
    issue_fields.update({"summary": title})
    issue_fields.update({"assignee": assignee})
    issue_fields.update({"reporter": reporter})

    description = Template(CASE_ISSUE_SUMMARY_TEMPLATE).render(
        assignee_username=assignee_username,
        case_priority=case_priority,
        case_severity=case_severity,
        case_type=case_type,
        description=description,
        document_weblink=document_weblink,
        resolution=resolution,
        storage_weblink=storage_weblink,
        dispatch_weblink=dispatch_weblink,
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


def create_fallback_ticket_incident(incident_id: int, project: Project):
    resource_id = f"dispatch-{project.organization.slug}-{project.slug}-{incident_id}"

    return {
        "resource_id": resource_id,
        "weblink": f"{DISPATCH_UI_URL}/{project.organization.name}/incidents/{resource_id}?project={project.name}",
        "resource_type": "jira-error-ticket",
    }


def create_fallback_ticket_case(case_id: int, project: Project):
    resource_id = f"dispatch-{project.organization.slug}-{project.slug}-{case_id}"

    return {
        "resource_id": resource_id,
        "weblink": f"{DISPATCH_UI_URL}/{project.organization.name}/cases/{resource_id}?project={project.name}",
        "resource_type": "jira-error-ticket",
    }


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
        commander_email: str,
        reporter_email: str,
        incident_type_plugin_metadata: dict = None,
        db_session=None,
    ):
        """Creates an incident Jira issue."""
        try:
            client = create_client(self.configuration)

            assignee = get_user_field(client, self.configuration, commander_email)

            reporter = assignee
            if reporter_email != commander_email:
                reporter = get_user_field(client, self.configuration, reporter_email)

            project_id, issue_type_name = process_plugin_metadata(incident_type_plugin_metadata)
            other_fields = create_dict_from_plugin_metadata(incident_type_plugin_metadata)

            if not project_id:
                project_id = self.configuration.default_project_id

            # NOTE: to support issue creation by project id or key
            project = {"id": project_id}
            if not project_id.isdigit():
                project = {"key": project_id}

            if not issue_type_name:
                issue_type_name = self.configuration.default_issue_type_name

            issuetype = {"name": issue_type_name}

            issue_fields = {
                "project": project,
                "issuetype": issuetype,
                "assignee": assignee,
                "reporter": reporter,
                "summary": title.replace("\n", ""),
                **other_fields,
            }

            ticket = create(self.configuration, client, issue_fields)
        except Exception as e:
            log.exception(
                f"Failed to create Jira ticket for incident_id: {incident_id}. "
                f"Creating incident ticket with core plugin instead. Error: {e}"
            )
            # fall back to creating a ticket without the plugin
            incident = incident_service.get(db_session=db_session, incident_id=incident_id)
            ticket = create_fallback_ticket_incident(
                incident_id=incident.id, project=incident.project
            )

        return ticket

    def update(
        self,
        ticket_id: str,
        title: str,
        description: str,
        incident_type: str,
        incident_severity: str,
        incident_priority: str,
        status: str,
        commander_email: str,
        reporter_email: str,
        conversation_weblink: str,
        document_weblink: str,
        storage_weblink: str,
        conference_weblink: str,
        dispatch_weblink: str,
        cost: float,
        incident_type_plugin_metadata: dict = None,
    ):
        """Updates an incident Jira issue."""
        client = create_client(self.configuration)

        assignee = get_user_field(client, self.configuration, commander_email)

        reporter = assignee
        if reporter_email != commander_email:
            reporter = get_user_field(client, self.configuration, reporter_email)

        commander_username = get_email_username(commander_email)

        issue = client.issue(ticket_id)
        issue_fields = create_incident_issue_fields(
            title=title,
            description=description,
            incident_type=incident_type,
            incident_severity=incident_severity,
            incident_priority=incident_priority,
            assignee=assignee,
            reporter=reporter,
            commander_username=commander_username,
            conversation_weblink=conversation_weblink,
            document_weblink=document_weblink,
            storage_weblink=storage_weblink,
            conference_weblink=conference_weblink,
            dispatch_weblink=dispatch_weblink,
            cost=cost,
        )

        return update(self.configuration, client, issue, issue_fields, status)

    def update_metadata(
        self,
        ticket_id: str,
        metadata: dict,
    ):
        """Updates the metadata of a Jira issue."""
        client = create_client(self.configuration)
        issue = client.issue(ticket_id)

        # check to make sure project id matches metadata
        project_id, issue_type_name = process_plugin_metadata(metadata)
        if project_id and issue.fields.project.key != project_id:
            log.warning(
                f"Project key mismatch between Jira issue {issue.fields.project.key} and metadata {project_id} for ticket {ticket_id}"
            )
            return
        other_fields = create_dict_from_plugin_metadata(metadata)
        issue_fields = {
            **other_fields,
        }
        if issue_type_name:
            issue_fields["issuetype"] = {"name": issue_type_name}

        issue.update(fields=issue_fields)

    def create_case_ticket(
        self,
        case_id: int,
        title: str,
        assignee_email: str,
        # reporter_email: str,
        case_type_plugin_metadata: dict = None,
        db_session=None,
    ):
        """Creates a case Jira issue."""
        try:
            client = create_client(self.configuration)

            assignee = get_user_field(client, self.configuration, assignee_email)
            # TODO(mvilanova): enable reporter email and replace assignee email
            # reporter = get_user_field(client, self.configuration, reporter_email)
            reporter = assignee

            project_id, issue_type_name = process_plugin_metadata(case_type_plugin_metadata)

            if not project_id:
                project_id = self.configuration.default_project_id

            project = {"id": project_id}
            if not project_id.isdigit():
                project = {"key": project_id}

            if not issue_type_name:
                issue_type_name = self.configuration.default_issue_type_name

            issuetype = {"name": issue_type_name}

            issue_fields = {
                "project": project,
                "issuetype": issuetype,
                "assignee": assignee,
                "reporter": reporter,
                "summary": title.replace("\n", ""),
            }

            ticket = create(self.configuration, client, issue_fields)
        except Exception as e:
            log.exception(
                (
                    f"Failed to create Jira ticket for case_id: {case_id}. "
                    f"Creating case ticket with core plugin instead. Error: {e}"
                )
            )
            # fall back to creating a ticket without the plugin
            case = case_service.get(db_session=db_session, case_id=case_id)
            ticket = create_fallback_ticket_case(case_id=case.id, project=case.project)

        return ticket

    def create_task_ticket(
        self,
        task_id: int,
        title: str,
        assignee_email: str,
        reporter_email: str,
        incident_ticket_key: str = None,
        task_plugin_metadata: dict = None,
        db_session=None,
    ):
        """Creates a task Jira issue."""
        client = create_client(self.configuration)

        assignee = get_user_field(client, self.configuration, assignee_email)
        reporter = get_user_field(client, self.configuration, reporter_email)

        project_id, issue_type_name = process_plugin_metadata(task_plugin_metadata)
        other_fields = create_dict_from_plugin_metadata(task_plugin_metadata)

        if not project_id:
            project_id = self.configuration.default_project_id

        project = {"id": project_id}
        if not project_id.isdigit():
            project = {"key": project_id}

        if not issue_type_name:
            issue_type_name = self.configuration.default_issue_type_name

        issuetype = {"name": issue_type_name}

        issue_fields = {
            "project": project,
            "issuetype": issuetype,
            "assignee": assignee,
            "reporter": reporter,
            "summary": title.replace("\n", ""),
            **other_fields,
        }

        issue = client.create_issue(fields=issue_fields)

        if incident_ticket_key:
            update = {
                "issuelinks": [
                    {
                        "add": {
                            "type": {
                                "name": "Relates",
                                "inward": "is related to",
                                "outward": "relates to",
                            },
                            "outwardIssue": {"key": incident_ticket_key},
                        }
                    }
                ]
            }
            issue.update(update=update)

        return {
            "resource_id": issue.key,
            "weblink": f"{self.configuration.browser_url}/browse/{issue.key}",
        }

    def update_case_ticket(
        self,
        ticket_id: str,
        title: str,
        description: str,
        resolution: str,
        case_type: str,
        case_severity: str,
        case_priority: str,
        status: str,
        assignee_email: str,
        # reporter_email: str,
        document_weblink: str,
        storage_weblink: str,
        dispatch_weblink: str,
        case_type_plugin_metadata: dict = None,
    ):
        """Updates a case Jira issue."""
        client = create_client(self.configuration)

        assignee = get_user_field(client, self.configuration, assignee_email)
        # TODO(mvilanova): enable reporter email and replace assignee email
        # reporter = get_user_field(client, self.configuration, reporter_email)
        reporter = assignee

        assignee_username = get_email_username(assignee_email)

        issue = client.issue(ticket_id)
        issue_fields = create_case_issue_fields(
            title=title,
            description=description,
            resolution=resolution,
            case_type=case_type,
            case_severity=case_severity,
            case_priority=case_priority,
            assignee=assignee,
            reporter=reporter,
            assignee_username=assignee_username,
            document_weblink=document_weblink,
            storage_weblink=storage_weblink,
            dispatch_weblink=dispatch_weblink,
        )

        return update(self.configuration, client, issue, issue_fields, status)

    def delete(self, ticket_id: str):
        """Deletes a Jira issue."""
        client = create_client(self.configuration)
        issue = client.issue(ticket_id)
        issue.delete()
