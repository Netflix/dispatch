"""
.. module: dispatch.plugins.dispatch_jira.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from jinja2 import Template
from jira import JIRA
from typing import Any, List
import ruamel.yaml as yaml
import requests

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_jira_custom as jira_plugin
from dispatch.plugins.bases import TicketPlugin


from .config import (
    JIRA_BROWSER_URL,
    JIRA_API_URL,
    JIRA_USERNAME,
    JIRA_PASSWORD,
    JIRA_PROJECT_KEY,
    JIRA_ISSUE_TYPE_ID,
    JIRA_ID_MAPPING_FILE_PATH,
)

# TODO: TO BE MOVED OUT
id_file_yaml = JIRA_ID_MAPPING_FILE_PATH

INCIDENT_TEMPLATE = """
{color:red}*CONFIDENTIAL -- Internal use only{color}*

*Summary*
{{description}}

*Incident Commander*
[~{{commander_username}}]

*Incident Resources*
[Incident Conversation|{{conversation_weblink}}]
[Incident Document|{{document_weblink}}]
[Incident Storage|{{storage_weblink}}]
[Incident Conference|{{conference_weblink}}]
"""

INCIDENT_PRIORITY_MAP = {
    "low": {"id": "28668"},
    "medium": {"id": "28669"},
    "high": {"id": "28670"},
    "info": {"id": "40461"},
}


def create_sec_issue(
    client: Any,
    title: str,
    priority: str,
    incident_type: str,
    commander_username: str,
    reporter_username: str,
):
    issue_fields = {
        "project": {"key": JIRA_PROJECT_KEY},
        # "issuetype": {"id": JIRA_ISSUE_TYPE_ID},
        "issuetype": {"name": JIRA_ISSUE_TYPE_ID},
        "summary": title,
        "assignee": {"id": commander_username},
        # "components": [{"name": incident_type}],
        "reporter": {"id": reporter_username},
        # "customfield_10551": INCIDENT_PRIORITY_MAP[priority.lower()],
    }

    return create(client, issue_fields, type=JIRA_PROJECT_KEY)


def create_issue_fields(
    title: str = None,
    description: str = None,
    incident_type: str = None,
    priority: str = None,
    commander_username: str = None,
    commander_username_id: str = None,
    reporter_username: str = None,
    conversation_weblink: str = None,
    document_weblink: str = None,
    storage_weblink: str = None,
    conference_weblink: str = None,
    labels: List[str] = None,
    cost: int = None,
):
    """Creates Jira issue fields."""
    issue_fields = {}

    if title:
        issue_fields.update({"summary": title})

    if (
        description
        and commander_username
        and document_weblink
        and conversation_weblink
        and storage_weblink
        and conference_weblink
    ):
        description = Template(INCIDENT_TEMPLATE).render(
            description=description,
            commander_username=commander_username,
            document_weblink=document_weblink,
            conference_weblink=conference_weblink,
            conversation_weblink=conversation_weblink,
            storage_weblink=storage_weblink,
        )
        issue_fields.update({"description": description})

    if commander_username_id:
        issue_fields.update({"assignee": {"id": commander_username_id}})

    if reporter_username:
        issue_fields.update({"reporter": {"id": reporter_username}})

    # if incident_type:
    #     issue_fields.update({"components": [{"name": incident_type}]})

    # if priority:
    #     issue_fields.update({"customfield_10551": INCIDENT_PRIORITY_MAP[priority.lower()]})

    if labels:
        issue_fields.update({"labels": labels})

    # if cost:
    #     issue_fields.update({"customfield_20250": str(cost)})

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

    print("update data:", data)
    return data


def link_issues(client: Any, link_type: str, issue_id_a: str, issue_id_b: str):
    """Links two Jira issues."""
    issue_key_a = client.issue(issue_id_b).key
    issue_key_b = client.issue(issue_id_b).key

    body = (
        f"Creating link of type {link_type} between Jira issue keys {issue_key_a} and {issue_key_b}"
    )

    client.create_issue_link(
        type=link_type, inwardIssue=issue_key_a, outwardIssue=issue_key_b, comment={"body": body}
    )

    return {
        "key_a": issue_key_a,
        "link_a": f"{JIRA_BROWSER_URL}/browse/{issue_key_a}",
        "key_b": issue_key_b,
        "link_b": f"{JIRA_BROWSER_URL}/browse/{issue_key_b}",
    }


def parse_yaml_file(filename: str, email_address: str) -> str:
    """Parse yaml file to get jira id"""
    with open(filename, 'r') as stream_config:
        try:
            out_config = yaml.load(stream_config, Loader=yaml.Loader)
        except IOError:
            raise Exception('yaml file: %s not found!', id_file_yaml)
        user = [v for k, v in out_config['email'].items() if k == email_address]
        if user:
            return ''.join(user)
        else:
            return out_config['default_account_id']


def get_id_from_email(email_address: str) -> str:
    """
    Returns jira account id based on email
    If no contact person does not exist set default assignee
    This is to address:
    https://community.atlassian.com/t5/Jira-questions/The-query-parameter-username-is-not-supported-in-GDPR-strict/qaq-p/1345106
    """
    """file from github will be the final file"""
    file_to_download = 'id_file.yaml'
    if 'raw' in id_file_yaml:
        print('downloading')
        try:
            r = requests.get(id_file_yaml)
            open(file_to_download, 'wb').write(r.content)
        except IOError as err:
            print("error downloading file from git: {0}".format(id_file_yaml))
            pass
        return parse_yaml_file(file_to_download, email_address)

    else:
        return parse_yaml_file(file_to_download, email_address)


def get_user_name(email):
    """Returns username part of email, if valid email is provided."""
    if "@" in email:
        return email.split("@")[0]
    return email


def get_user_id_from_jira(email):
    """Returns username part of email, if valid email is provided."""
    return get_id_from_email(email)


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class JiraCustomTicketPlugin(TicketPlugin):
    title = "Jira Cloud Plugin"
    slug = "jira-ticket-custom"
    description = "Uses Jira Cloud to help manage external tickets."
    version = jira_plugin.__version__

    author = "Varun Tomar"
    author_url = "https://github.com/tomarv2/dispatch.git"

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
        """Creates a Jira ticket."""
        client = JIRA(str(JIRA_API_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))
        commander_username = get_user_id_from_jira(commander)
        reporter_username = get_user_id_from_jira(reporter)
        return create_sec_issue(
            client, title, incident_priority, incident_type, commander_username, reporter_username
        )

    def update(
        self,
        ticket_id: str,
        title: str = None,
        description: str = None,
        incident_type: str = None,
        priority: str = None,
        status: str = None,
        commander_email: str = None,
        reporter_email: str = None,
        conversation_weblink: str = None,
        conference_weblink: str = None,
        document_weblink: str = None,
        storage_weblink: str = None,
        labels: List[str] = None,
        cost: int = None,
        incident_type_plugin_metadata: dict = {},
    ):
        """Updates Jira ticket fields."""
        commander_username = get_user_name(commander_email) if commander_email else None
        commander_username_id = get_user_id_from_jira(commander_email) if commander_email else None
        reporter_username = get_user_id_from_jira(reporter_email) if reporter_email else None

        client = JIRA(str(JIRA_API_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))

        issue = client.issue(ticket_id)
        issue_fields = create_issue_fields(
            title=title,
            description=description,
            incident_type=incident_type,
            priority=priority,
            commander_username=commander_username,
            commander_username_id=commander_username_id,
            reporter_username=reporter_username,
            conversation_weblink=conversation_weblink,
            conference_weblink=conference_weblink,
            document_weblink=document_weblink,
            storage_weblink=storage_weblink,
            labels=labels,
            cost=cost,
        )
        print("update: ", update(client, issue, issue_fields, status))
        return update(client, issue, issue_fields, status)