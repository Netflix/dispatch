"""
.. module: dispatch.plugins.google_drive.task
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import re
from typing import Any, List, Dict

from dispatch.config import DISPATCH_DOMAIN

from .drive import get_file, list_comments
from .config import GOOGLE_DOMAIN


def get_assignees(content: str) -> List[str]:
    """Gets assignees from comment."""
    regex = r"(?<=\+).*?(?=\@)"
    matches = re.finditer(regex, content, re.DOTALL)
    return [f"{m.group()}@{DISPATCH_DOMAIN}" for m in matches]


def parse_comment(content: str) -> Dict:
    """Parses a comment into it's various parts."""
    assignees = get_assignees(content)
    return {"assignees": assignees}


def get_task_status(task: dict):
    """Gets the current status from task."""
    status = {"resolved": False, "resolved_at": "", "resolved_by": ""}
    if task.get("resolved"):
        for r in task["replies"]:
            if r.get("action") == "resolve":
                status["resolved_by"] = r["author"]["displayName"]
                status["resolved_at"] = r["createdTime"]
                return status


def filter_comments(comments: List[Any]):
    """Filters comments for tasks."""
    return [c for c in comments if parse_comment(c["content"])["assignees"]]


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
        assignees = get_assignees(t["content"])
        description = (t.get("quotedFileContent", {}).get("value", ""),)

        task_meta = {
            "task": {
                "id": t["id"],
                "status": status,
                "description": description,
                "owner": t["author"]["displayName"],
                "created_at": t["createdTime"],
                "assignees": assignees,
                "web_link": f'https://docs.google.com/a/{GOOGLE_DOMAIN}/document/d/{file_id}/edit?disco={t["id"]}',
            }
        }

        tasks.append({**document_meta, **task_meta})

    return tasks
