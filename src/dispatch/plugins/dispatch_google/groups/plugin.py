"""
.. module: dispatch.plugins.dispatch_google_groups.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
import time
from enum import Enum
from typing import Any, List

from googleapiclient.errors import HttpError
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import ParticipantGroupPlugin
from dispatch.plugins.dispatch_google import groups as google_group_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import (
    DWD_ENABLED,
    GOOGLE_CUSTOMER_ID,
    GOOGLE_DOMAIN,
    GOOGLE_USER_OVERRIDE,
)

log = logging.getLogger(__name__)


class GroupLabels(str, Enum):
    google_group = "cloudidentity.googleapis.com/groups.discussion_forum"
    dynamic_groups = "cloudidentity.googleapis.com/groups.dynamic"
    security_groups = "cloudidentity.googleapis.com/groups.security"


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=2, max=5),
)
def make_call(
    client: Any,
    func: Any,
    delay: int = None,
    propagate_errors: bool = False,
    params: dict = {},
    **kwargs,
):
    """Make an google client api call."""
    try:
        # Get the request, so that we can modify the request params
        request = getattr(client, func)(**kwargs)

        # Set the request params based on the methodId property
        if request.methodId == "cloudidentity.groups.create":
            log.debug("Using param initialGroupConfig=WITH_INITIAL_OWNER.")
            request.uri += "&initialGroupConfig=WITH_INITIAL_OWNER"
        elif request.methodId == "cloudidentity.groups.lookup":
            log.debug(f"Using param groupKey.id={params['group_email']}.")
            request.uri += f"&groupKey.id={params['group_email']}"
        elif request.methodId == "cloudidentity.groups.memberships.lookup":
            log.debug(f"Using param memberKey.id={params['member_email']}.")
            request.uri += f"&memberKey.id={params['member_email']}"

        # Execute the request
        data = request.execute()

        if delay:
            time.sleep(delay)

        return data
    except HttpError as e:
        if propagate_errors:
            raise e
        else:
            log.error(e.content.decode())

        raise TryAgain


def get_group_name(client: Any, group_email: str):
    # Pass the group email via the params dictionary
    response = make_call(client.groups(), "lookup", params={"group_email": group_email})
    return response.get("name")


def get_group_membership_name(client: Any, group_email: str, member_email: str):
    group_name = get_group_name(client, group_email)
    response = make_call(
        client.groups().memberships(),
        "lookup",
        # Pass the member email via the params dictionary
        params={"member_email": member_email},
        parent=group_name,
    )
    return response.get("name")


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
    group_name = get_group_name(client, group_key)

    if role == "OWNER":
        members = expand_group(client, group_key)

    for m in members:
        body = {"preferredMemberKey": {"id": m}, "roles": {"name": role}}
        if DWD_ENABLED and GOOGLE_USER_OVERRIDE:
            log.warning("GOOGLE_USER_OVERIDE set and DWD is enabled. Using override.")
            body["preferredMemberKey"] = GOOGLE_USER_OVERRIDE

        try:
            make_call(
                client.groups().memberships(),
                "create",
                parent=group_name,
                body=body,
                propagate_errors=True,
            )
            log.debug(f"Participant {m} successfully added to {group_key} group")
        except HttpError as e:
            #  we are okay with duplication errors upon insert
            if e.resp.status in [409]:
                log.debug(
                    f"Member already exists in google group. GroupKey={group_key} Body={body}"
                )
                continue

            log.debug(f"Error adding group member. GroupKey={group_key} Body={body} ")


def remove_member(client: Any, group_email: str, member_email: str):
    """Removes member from google group."""
    membership_name = get_group_membership_name(client, group_email, member_email)
    return make_call(client.groups().memberships(), "delete", name=membership_name)


def list_members(client: Any, group_email: str, **kwargs):
    """Lists all members of google group."""
    group_name = get_group_name(client, group_email)
    return make_call(client.groups().memberships(), "list", parent=group_name)


def create_group(client: Any, name: str, group_email: str, description: str):
    """Creates a new google group."""
    body = {
        "parent": f"customers/{GOOGLE_CUSTOMER_ID}",
        "groupKey": {"id": group_email},
        "displayName": name,
        "description": description,
        "labels": {GroupLabels.google_group: ""},
    }
    return make_call(client.groups(), "create", body=body, delay=3)


def delete_group(client: Any, group_email: str, **kwargs):
    """Delete a google group."""
    group_name = get_group_name(client, group_email)
    return make_call(client.groups(), "delete", name=group_name, **kwargs)


def list_groups(client: Any, **kwargs):
    """Lists all google groups available."""
    parent = f"customers/{GOOGLE_CUSTOMER_ID}"
    return make_call(client.groups(), "list", parent=parent, **kwargs)


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
            "https://www.googleapis.com/auth/cloud-identity.groups",
        ]

    def create(
        self, name: str, participants: List[str], description: str = None, role: str = "MEMBER"
    ):
        """Creates a new Google Group."""
        client = get_service("cloudidentity", "v1", self.scopes)
        group_key = f"{name.lower()}@{GOOGLE_DOMAIN}"

        if not description:
            description = "Group automatically created by Dispatch."

        group_response = create_group(client, name, group_key, description)
        group = group_response["response"]

        group["email"] = group["groupKey"]["id"]
        group_email_prefix = group["email"].split("@")[0]
        group["group_name"] = group["name"]
        group["id"] = group["name"].split("/")[1]
        group["name"] = group_email_prefix

        log.debug(f"Group created: {group}")
        for p in participants:
            add_member(client, group_key, p, role)
        group.update(
            {"weblink": f"https://groups.google.com/a/{GOOGLE_DOMAIN}/g/{group_email_prefix}"}
        )
        return group

    def add(self, email: str, participants: List[str], role: str = "MEMBER"):
        """Adds participants to an existing Google Group."""
        client = get_service("cloudidentity", "v1", self.scopes)
        for p in participants:
            add_member(client, email, p, role)

    def remove(self, email: str, participants: List[str]):
        """Removes participants from an existing Google Group."""
        client = get_service("cloudidentity", "v1", self.scopes)
        for p in participants:
            remove_member(client, email, p)

    def list(self, email: str):
        """Lists members from an existing Google Group."""
        client = get_service("cloudidentity", "v1", self.scopes)
        members = list_members(client, email)
        return [m["email"] for m in members["members"]]

    def delete(self, email: str):
        """Deletes an existing Google group."""
        client = get_service("cloudidentity", "v1", self.scopes)
        delete_group(client, email)
