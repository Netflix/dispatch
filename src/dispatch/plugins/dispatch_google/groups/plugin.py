"""
.. module: dispatch.plugins.dispatch_google_groups.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
import time
from typing import Any, List

from googleapiclient.errors import HttpError
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import ParticipantGroupPlugin
from dispatch.plugins.dispatch_google import groups as google_group_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import GOOGLE_USER_OVERRIDE, GOOGLE_DOMAIN

log = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=2, max=5),
)
def make_call(client: Any, func: Any, delay: int = None, propagate_errors: bool = False, **kwargs):
    """Make an google client api call."""
    try:
        data = getattr(client, func)(**kwargs).execute()

        if delay:
            time.sleep(delay)

        return data
    except HttpError as e:
        if propagate_errors:
            raise e
        else:
            log.error(e.content.decode())

        raise TryAgain


def expand_group(client: Any, group_key: str):
    """Determines if an email is really a dl."""
    # NOTE: Google Groups does not support other DLs as Group owners
    # https://stackoverflow.com/questions/31552146/group-as-owner-or-manager-fails-with-400-error
    try:
        response = list_members(client, group_key, propagate_errors=True)
        if response.get("members"):
            return [x["email"] for x in response.get("members", [])]
    except HttpError as e:
        if e.resp.status == 404:
            pass

    return []


def add_member(client: Any, group_key: str, email: str, role: str):
    """Adds a member to a google group."""
    members = [email]

    if role == "OWNER":
        members = expand_group(client, group_key)

    for m in members:
        body = {"email": m, "role": role}
        if GOOGLE_USER_OVERRIDE:
            log.warning("GOOGLE_USER_OVERIDE set. Using override.")
            body["email"] = GOOGLE_USER_OVERRIDE

        try:
            make_call(
                client.members(), "insert", groupKey=group_key, body=body, propagate_errors=True
            )
        except HttpError as e:
            #  we are okay with duplication errors upon insert
            if e.resp.status in [409]:
                log.debug(
                    f"Member already exists in google group. GroupKey={group_key} Body={body}"
                )
                continue

            log.debug(f"Error adding group member. GroupKey={group_key} Body={body} ")


def remove_member(client: Any, group_key: str, email: str):
    """Removes member from google group."""
    return make_call(client.members(), "delete", groupKey=group_key, memberKey=email)


def list_members(client: Any, group_key: str, **kwargs):
    """Lists all members of google group."""
    return make_call(client.members(), "list", groupKey=group_key, **kwargs)


def create_group(client: Any, name: str, email: str, description: str):
    """Creates a new google group."""
    body = {"email": email, "name": name, "adminCreated": False, "description": description}
    return make_call(client.groups(), "insert", body=body, delay=3)


def delete_group(client: Any, group_key: str, **kwargs):
    """Delete a google group."""
    return make_call(client.groups(), "delete", groupKey=group_key, **kwargs)


def list_groups(client: Any, **kwargs):
    """Lists all google groups available."""
    return make_call(client.groups(), "list", **kwargs)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleGroupParticipantGroupPlugin(ParticipantGroupPlugin):
    title = "Google Group Plugin - Participant Group Management"
    slug = "google-group-participant-group"
    description = "Uses Google Groups to help manage participant membership."
    version = google_group_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    _schema = None

    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/apps.groups.settings",
        ]

    def create(
        self, name: str, participants: List[str], description: str = None, role: str = "MEMBER"
    ):
        """Creates a new Google Group."""
        client = get_service("admin", "directory_v1", self.scopes)
        group_key = f"{name.lower()}@{GOOGLE_DOMAIN}"

        if not description:
            description = "Group automatically created by Dispatch."

        group = create_group(client, name, group_key, description)

        for p in participants:
            add_member(client, group_key, p, role)

        group.update(
            {
                "weblink": f"https://groups.google.com/a/{GOOGLE_DOMAIN}/forum/#!forum/{group['name']}"
            }
        )
        return group

    def add(self, email: str, participants: List[str], role: str = "MEMBER"):
        """Adds participants to an existing Google Group."""
        client = get_service("admin", "directory_v1", self.scopes)
        for p in participants:
            add_member(client, email, p, role)

    def remove(self, email: str, participants: List[str]):
        """Removes participants from an existing Google Group."""
        client = get_service("admin", "directory_v1", self.scopes)
        for p in participants:
            remove_member(client, email, p)

    def list(self, email: str):
        """Lists members from an existing Google Group."""
        client = get_service("admin", "directory_v1", self.scopes)
        members = list_members(client, email)
        return [m["email"] for m in members["members"]]

    def delete(self, email: str):
        """Deletes an existing Google group."""
        client = get_service("admin", "directory_v1", self.scopes)
        delete_group(client, email)
