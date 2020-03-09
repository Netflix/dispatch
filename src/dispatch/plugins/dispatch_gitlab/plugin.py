"""
.. module: dispatch.plugins.dispatch_gitlab.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import datetime
import pytz
import uuid

from jinja2 import Template
import gitlab
from typing import Any, List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_gitlab as gitlab_plugin
from dispatch.plugins.bases import TicketPlugin

from .config import (
    GITLAB_BROWSER_URL,
    GITLAB_API_URL,
    GITLAB_AUTH_KEY,
    GITLAB_INCIDENT_PROJECT_ID
  )

INCIDENT_TEMPLATE = """
# CONFIDENTIAL -- Internal use only

## Summary
{{description}}

## Incident Commander
@{{commander_username}}

## Incident Resources
* [Incident Conversation]({{conversation_weblink}})
* [Incident Document]({{document_weblink}})
* [Incident Storage]({{storage_weblink}})

*Reported by : @{{reporter_username}}*
"""

INCIDENT_INIT_TEMPLATE = """
# CONFIDENTIAL -- Internal use only

## Summary
This incident is getting updated shortly

##
Commander : @{{commander_username}}
*Reported by : @{{reporter_username}}*
"""

INCIDENT_PRIORITY_MAP = {
    "low": "Incident::Low",
    "medium": "Incident::Medium",
    "high": "Incident::High",
    "info": "Incident::Info",
    "vulnerability": "Incident::vulnerability"
}

def create_incident_issue(gitlab, title, incident_priority, incident_type, commander_username, reporter_username,):
    """Generates an incident ticket in gitlab"""
    project = gitlab.projects.get(GITLAB_INCIDENT_PROJECT_ID)
    return project.issues.create({
      'title': title,
      'labels': INCIDENT_PRIORITY_MAP[incident_priority.lower()],
      'description': Template(INCIDENT_INIT_TEMPLATE).render(
            commander_username=commander_username,
            reporter_username=reporter_username
        )
    }).iid

def update_issue(issue, title, description, incident_type, priority, commander_username, reporter_username, conversation_weblink, document_weblink, storage_weblink, labels, cost, status):
  if status.lower() == 'closed':
    issue.closed = True

  if title:
      issue.title = title

  if (
      description
      and commander_username
      and document_weblink
      and conversation_weblink
      and storage_weblink
  ):
      description = Template(INCIDENT_TEMPLATE).render(
          description=description,
          commander_username=commander_username,
          reporter_username=reporter_username,
          document_weblink=document_weblink,
          conversation_weblink=conversation_weblink,
          storage_weblink=storage_weblink,
      )
      issue.description = description

  if commander_id:
    issue.assignee_ids = [commander_id]

  if labels:
    issue.labels = labels

  if priority:
    issue.labels = issue.labels + "," + INCIDENT_PRIORITY_MAP[incident_priority.lower()]

  if incident_type:
    issue.labels = issue.labels + "," + INCIDENT_TYPE_MAP[incident_type.lower()]


def get_user_name(email):
    """Returns username part of email, if valid email is provided."""
    if "@" in email:
        return email.split("@")[0]
    return email

def get_user_id(client, username):
  try:
    return client.users.list(username=username)[0].id
  except expression as identifier:
    return None

@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class GitlabTicketPlugin(TicketPlugin):
    title = "Gitlab - Ticket"
    slug = "gitlab-ticket"
    description = "Uses Gitlab as an external ticket creator."
    version = gitlab_plugin.__version__

    author = "Xavier De Cock"
    author_url = "https://github.com/xdecock/dispatch.git"

    _schema = None

    def __init__(self):
        self.client = gitlab.Gitlab(GITLAB_API_URL, private_token=GITLAB_AUTH_KEY)

    def create(
        self, title: str, incident_type: str, incident_priority: str, commander: str, reporter: str
    ):
        """Creates a Gitlab ticket."""
        commander_username = get_user_name(commander)
        reporter_username = get_user_name(reporter)
        return create_incident_issue(
            self.client,
            title,
            incident_priority,
            incident_type,
            commander_username,
            reporter_username,
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
        document_weblink: str = None,
        storage_weblink: str = None,
        labels: List[str] = None,
        cost: str = None,
    ):
        project_id = GITLAB_INCIDENT_PROJECT_ID

        """Updates Gitlab ticket fields."""
        commander_username = get_user_name(commander_email) if commander_email else None
        reporter_username = get_user_name(reporter_email) if reporter_email else None

        issue = self.client.projects.get(project_id).issues.get(ticket_id)
        update_issue(
          issue = issue,
          title = title,
          description = description,
          incident_type = incident_type,
          priority = priority,
          commander_username = commander_username,
          commander_id = get_user_id(self.client, commander_username)
          reporter_username = reporter_username,
          conversation_weblink = conversation_weblink,
          document_weblink = document_weblink,
          storage_weblink = storage_weblink,
          labels = labels,
          cost = cost,
          status = status
        )
        return issue.save()
