"""
.. module: dispatch.plugins.google_drive.task
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import re
import logging
from typing import Any, List

from dispatch.task.enums import TaskStatus
from enum import Enum

from .drive import get_activity, get_comment, get_person

log = logging.getLogger(__name__)


class CommentTypes(str, Enum):
    assignment = "assignment"
    post = "post"


class PostSubTypes(str, Enum):
    subtype_unspecified = "SUBTYPE_UNSPECIFIED"
    added = "ADDED"
    deleted = "DELETED"
    reply_added = "REPLY_ADDED"
    reply_deleted = "REPLY_DELETED"
    resolved = "RESOLVED"
    reopened = "REOPENED"


class AssignmentSubTypes(str, Enum):
    subtype_unspecified = "SUBTYPE_UNSPECIFIED"
    added = "ADDED"
    deleted = "DELETED"
    reply_added = "REPLY_ADDED"
    reply_deleted = "REPLY_DELETED"
    resolved = "RESOLVED"
    reopened = "REOPENED"
    reassigned = "REASSIGNED"


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


def get_user_email(client: Any, person_id: str) -> str:
    """Resolves the email address for the actor of the activity."""
    try:
        # fetch the email from the people api
        person_data = get_person(client, person_id)
        email_address = person_data["emailAddresses"][0]["value"]
    except KeyError:
        return "unknown@example.com"

    return email_address


def get_task_activity(
    activity_client: Any, comment_client: Any, people_client: Any, file_id: str, lookback: int = 60
):
    """Gets a files comment activity and filters for task related events."""
    activities = get_activity(activity_client, file_id, lookback=lookback)

    tasks = []
    for a in sorted(activities, key=lambda time: time["timestamp"]):
        # process an assignment activity
        if a["primaryActionDetail"]["comment"].get(CommentTypes.assignment):
            subtype = a["primaryActionDetail"]["comment"][CommentTypes.assignment]["subtype"]
            discussion_id = a["targets"][0]["fileComment"]["legacyDiscussionId"]

            task = {"resource_id": discussion_id}

            # we assume the person doing the assignment to be the creator of the task
            creator_person_id = a["actors"][0]["user"]["knownUser"]["personName"]
            task["creator"] = {
                "individual": {"email": get_user_email(people_client, creator_person_id)}
            }

            # we create a new task when comment has an assignment added to it
            if subtype == AssignmentSubTypes.added:
                # we need to fetch the comment data
                discussion_id = a["targets"][0]["fileComment"]["legacyDiscussionId"]
                comment = get_comment(comment_client, file_id, discussion_id)

                task["description"] = comment.get("quotedFileContent", {}).get("value", "")

                task["tickets"] = get_tickets(comment["replies"])

                # we only associate the current assignee event if multiple of people are mentioned (NOTE: should we also associated other mentions?)
                assignee_person_id = a["primaryActionDetail"]["comment"][CommentTypes.assignment][
                    "assignedUser"
                ]["knownUser"]["personName"]
                task["assignees"] = [
                    {"individual": {"email": get_user_email(people_client, assignee_person_id)}}
                ]

                # this is when the user was assigned (making it into a task, not when the inital comment was created)
                task["created_at"] = a["timestamp"]

                # this is the deep link to the associated comment
                task["weblink"] = a["targets"][0]["fileComment"]["linkToDiscussion"]

            elif subtype == AssignmentSubTypes.reply_added:
                # check to see if there are any linked tickets
                comment_id = a["targets"][0]["fileComment"]["legacyDiscussionId"]
                comment = get_comment(comment_client, file_id, comment_id)
                task["tickets"] = get_tickets(comment["replies"])

            elif subtype == AssignmentSubTypes.deleted:
                task["status"] = TaskStatus.resolved

            elif subtype == AssignmentSubTypes.resolved:
                task["status"] = TaskStatus.resolved

            elif subtype == AssignmentSubTypes.reassigned:
                assignee_person_id = a["primaryActionDetail"]["comment"][CommentTypes.assignment][
                    "assignedUser"
                ]["knownUser"]["personName"]
                task["assignees"] = [
                    {"individual": {"email": get_user_email(people_client, assignee_person_id)}}
                ]

            elif subtype == AssignmentSubTypes.reopened:
                task["status"] = TaskStatus.open

            tasks.append(task)
    return tasks
