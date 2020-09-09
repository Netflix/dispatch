"""
.. module: dispatch.plugins.google_drive.task
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import re
import logging
from typing import Any, List, Dict

from dispatch.task.models import TaskStatus
from dispatch.plugins.dispatch_google.config import GOOGLE_DOMAIN

from .drive import get_file, list_comments

log = logging.getLogger(__name__)


def get_assignees(content: str) -> List[str]:
    """Gets assignees from comment."""
    regex = r"\@([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    matches = re.findall(regex, content)
    return [m for m in matches]


def parse_comment(content: str) -> Dict:
    """Parses a comment into it's various parts."""
    assignees = get_assignees(content)
    return {"assignees": assignees}


def get_task_status(task: dict):
    """Gets the current status from a task."""
    status = {"status": TaskStatus.open, "resolved_at": None, "resolved_by": None}
    if task.get("resolved"):
        for r in task["replies"]:
            if r.get("action") == "resolve":
                status["resolved_by"] = r["author"]["displayName"]
                status["resolved_at"] = r["createdTime"]
                status["status"] = TaskStatus.resolved
    return status


def filter_comments(comments: List[Any]):
    """Filters comments for tasks."""
    return [c for c in comments if parse_comment(c["content"])["assignees"]]


def find_urls(text: str) -> List[str]:
    """Finds a url in a text blob."""
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, text)
    return [x[0] for x in url]


def get_tickets(replies: List[dict]):
    """Fetches urls/tickets from task replies."""
    tickets = []
    for r in replies:
        if r.get("content"):
            for url in find_urls(r["content"]):
                tickets.append({"web_link": url})
    return tickets


# NOTE We have to use `displayName` instead of `emailAddress` because it's
# not visible to us. We should ask rcerda about why that might be.
def list_tasks(client: Any, file_id: str):
    """Returns all tasks in file."""
    doc = get_file(client, file_id)

    document_meta = {"document": {"id": file_id, "name": doc["name"]}}

    all_comments = list_comments(client, file_id)
    task_comments = filter_comments(all_comments)

    tasks = []
    for t in task_comments:
        status = get_task_status(t)
        assignees = [{"individual": {"email": x}} for x in get_assignees(t["content"])]
        description = t.get("quotedFileContent", {}).get("value", "")
        tickets = get_tickets(t["replies"])

        # this is a dirty hack because google doesn't return emailAddresses for comments
        # complete with conflicting docs
        # https://developers.google.com/drive/api/v2/reference/comments#resource
        from dispatch.database import SessionLocal
        from dispatch.individual.models import IndividualContact

        db_session = SessionLocal()
        owner = (
            db_session.query(IndividualContact)
            .filter(IndividualContact.name == t["author"]["displayName"])
            .first()
        )

        if not owner:
            log.error(f"Unable to identify owner by displayName: {t['author']['displayName']}")
            continue

        db_session.close()

        task_meta = {
            "task": {
                "resource_id": t["id"],
                "description": description,
                "owner": {"individual": {"email": owner.email}},
                "created_at": t["createdTime"],
                "assignees": assignees,
                "tickets": tickets,
                "weblink": f'https://docs.google.com/a/{GOOGLE_DOMAIN}/document/d/{file_id}/edit?disco={t["id"]}',
            }
        }

        task_meta["task"].update(status)

        tasks.append({**document_meta, **task_meta})

    return tasks
