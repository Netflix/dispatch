"""
.. module: dispatch.plugins.dispatch_slack.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from datetime import datetime, timezone
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt
from typing import Any, Dict, List, Optional
import functools
import logging
import re
import slack
import time

from .config import SLACK_API_BOT_TOKEN, SLACK_APP_USER_SLUG, SLACK_USER_ID_OVERRIDE


log = logging.getLogger(__name__)


class NoConversationFoundException(Exception):
    pass


def create_slack_client(run_async: bool = False):
    """Creates a Slack Web API client."""
    return slack.WebClient(token=SLACK_API_BOT_TOKEN, run_async=run_async)


def contains_numbers(string):
    return any(char.isdigit() for char in string)


def resolve_user(client: Any, user_id: str):
    """Attempts to resolve a user object regardless if email, id, or prefix."""
    if SLACK_USER_ID_OVERRIDE:
        log.warning("SLACK_USER_ID_OVERIDE set. Using override.")
        return {"id": SLACK_USER_ID_OVERRIDE}

    if "@" in user_id:
        return get_user_info_by_email(client, user_id)

    return {"id": user_id}


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


def paginated(data_key):
    def decorator(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            results = []

            while True:
                response = func(*args, **kwargs)
                results += response[data_key]

                # stop if we hit an empty string
                next_cursor = response["response_metadata"]["next_cursor"]
                if not next_cursor:
                    break

                kwargs.update({"cursor": next_cursor})

            return results

        return decorated_function

    return decorator


def time_pagination(data_key):
    def decorator(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            results = []

            while True:
                response = func(*args, **kwargs)
                results += response[data_key]

                # stop if we hit an empty string
                if not response["has_more"]:
                    break

                kwargs.update({"latest": response["messages"][0]["ts"]})

            return results

        return decorated_function

    return decorator


# NOTE I don't like this but slack client is annoying (kglisson)
SLACK_GET_ENDPOINTS = ["users.lookupByEmail", "users.info", "conversations.history"]


@retry(stop=stop_after_attempt(5), retry=retry_if_exception_type(TryAgain))
def make_call(client: Any, endpoint: str, **kwargs):
    """Make an slack client api call."""

    try:
        if endpoint in SLACK_GET_ENDPOINTS:
            response = client.api_call(endpoint, http_verb="GET", params=kwargs)
        else:
            response = client.api_call(endpoint, json=kwargs)
    except slack.errors.SlackApiError as e:
        log.error(f"SlackError. Response: {e.response} Endpoint: {endpoint} kwargs: {kwargs}")

        # NOTE we've seen some eventual consistency problems with channel creation
        if e.response["error"] == "channel_not_found":
            raise TryAgain

        # NOTE we've seen some eventual consistency problems after adding users to a channel
        if e.response["error"] == "user_not_in_channel":
            raise TryAgain

        if e.response.headers.get("Retry-After"):
            wait = int(e.response.headers["Retry-After"])
            log.info(f"SlackError: Rate limit hit. Waiting {wait} seconds.")
            time.sleep(wait)
            raise TryAgain
        else:
            raise e

    return response


async def make_call_async(client: Any, endpoint: str, **kwargs):
    """Make an slack client api call."""

    try:
        if endpoint in SLACK_GET_ENDPOINTS:
            response = await client.api_call(endpoint, http_verb="GET", params=kwargs)
        else:
            response = await client.api_call(endpoint, json=kwargs)
    except slack.errors.SlackApiError as e:
        log.error(f"SlackError. Response: {e.response} Endpoint: {endpoint} kwargs: {kwargs}")

        if e.response.headers.get("Retry-After"):
            wait = int(response.headers["Retry-After"])
            log.info(f"SlackError: Rate limit hit. Waiting {wait} seconds.")
            time.sleep(wait)
            raise TryAgain
        else:
            raise e

    return response


@paginated("channels")
def list_conversations(client: Any, **kwargs):
    return make_call(client, "conversations.list", types="private_channel", **kwargs)


# @time_pagination("messages")
def list_conversation_messages(client: Any, conversation_id: str, **kwargs):
    """Returns a list of conversation messages."""
    return make_call(client, "conversations.history", channel=conversation_id, **kwargs)


@functools.lru_cache()
def get_user_info_by_id(client: Any, user_id: str):
    """Gets profile information about a user by id."""
    return make_call(client, "users.info", user=user_id)["user"]


@functools.lru_cache()
async def get_user_info_by_id_async(client: Any, user_id: str):
    """Gets profile information about a user by id."""
    return (await make_call_async(client, "users.info", user=user_id))["user"]


@functools.lru_cache()
def get_user_info_by_email(client: Any, email: str):
    """Gets profile information about a user by email."""
    return make_call(client, "users.lookupByEmail", email=email)["user"]


def get_user_email(client: Any, user_id: str):
    """Gets the user's email."""
    return get_user_info_by_id(client, user_id)["profile"]["email"]


async def get_user_email_async(client: Any, user_id: str):
    """Gets the user's email."""
    return (await get_user_info_by_id_async(client, user_id))["profile"]["email"]


def get_user_username(client: Any, user_id: str):
    """Gets the user's username."""
    return get_user_email(client, user_id).split("@")[0]


def get_user_avatar_url(client: Any, email: str):
    """Gets the user's avatar url."""
    return get_user_info_by_email(client, email)["profile"]["image_512"]


def get_escaped_user_from_command(command_text: str):
    """Gets escaped user sent to Slack command."""
    return re.match(r"<@(?P<user_id>\w+)\|(?P<user_name>\w+)>", command_text).group("user_id")


# note this will get slower over time, we might exclude archived to make it sane
def get_conversation_by_name(client: Any, name: str):
    """Fetches a conversation by name."""
    for c in list_conversations(client):
        if c["name"] == name:
            return c


def get_conversation_messages_by_reaction(client: Any, conversation_id: str, reaction: str):
    """Fetches messages from a conversation by reaction type."""
    messages = []
    for m in list_conversation_messages(client, conversation_id):
        if "reactions" in m and m["reactions"][0]["name"] == reaction and m["text"].strip():
            messages.insert(
                0,
                {
                    "datetime": datetime.fromtimestamp(float(m["ts"]))
                    .astimezone(timezone("America/Los_Angeles"))
                    .strftime("%Y-%m-%d %H:%M:%S"),
                    "message": m["text"],
                    "user": get_user_info_by_id(client, m["user"])["user"]["real_name"],
                },
            )
    return messages


def set_conversation_topic(client: Any, conversation_id: str, topic: str):
    """Sets the topic of the specified conversation."""
    return make_call(client, "conversations.setTopic", channel=conversation_id, topic=topic)


def set_conversation_purpose(client: Any, conversation_id: str, purpose: str):
    """Sets the purpose of the specified conversation."""
    return make_call(client, "conversations.setPurpose", channel=conversation_id, purpose=purpose)


def create_conversation(client: Any, name: str, participants: List[str], is_private: bool = False):
    """Make a new slack conversation."""
    participants = list(set(participants))
    response = make_call(
        client,
        "conversations.create",
        name=name.lower(),  # slack disallows upperCase
        is_group=is_private,
        is_private=is_private,
        # user_ids=participants,  # NOTE this allows for 30 folks max
    )["channel"]

    add_users_to_conversation(client, response["id"], participants)

    return {
        "id": response["id"],
        "name": response["name"],
        "weblink": f"https://slack.com/app_redirect?channel={response['id']}",
    }


def close_conversation(client: Any, conversation_id):
    """Closes an existing conversation."""
    return make_call(client, "conversations.close", channel=conversation_id)


def archive_conversation(client: Any, conversation_id: str):
    """Archives an existing conversation."""
    return make_call(client, "conversations.archive", channel=conversation_id)


def add_users_to_conversation(client: Any, conversation_id: str, user_ids: List[str]):
    """Add users to conversation."""
    # NOTE this will trigger a member_joined_channel event, which we will capture and run the incident.incident_add_or_reactivate_participant_flow() as a result
    for c in chunks(user_ids, 30):  # NOTE api only allows 30 at a time.
        make_call(client, "conversations.invite", users=c, channel=conversation_id)


@paginated("members")
def get_conversation_members(
    client: Any, conversation_id: str, include_bots: bool = False, **kwargs
):
    response = make_call(client, "conversations.members", channel=conversation_id, **kwargs)

    details = []
    for m in response["members"]:
        details.append(make_call(client, "users.info", user=m)["user"])

    response["members"] = details
    return response


def get_conversation_details(client: Any, conversation_id):
    """Get conversation details."""
    return make_call(client, "conversations.info", channel=conversation_id)


def send_message(
    client: Any, conversation_id: str, text: str = None, blocks: Dict = None, persist: bool = False
):
    """Sends a message to the given conversation."""
    response = make_call(
        client, "chat.postMessage", channel=conversation_id, text=text, blocks=blocks
    )

    if persist:
        add_pin(client, response["channel"], response["ts"])

    return {"id": response["channel"], "timestamp": response["ts"]}


def send_ephemeral_message(
    client: Any, conversation_id: str, user_id: str, text: str, blocks: Optional[List] = None
):
    """Sends an ephemeral message to a user in a channel."""
    response = make_call(
        client,
        "chat.postEphemeral",
        channel=conversation_id,
        user=user_id,
        text=text,
        blocks=blocks,
    )

    return {"id": response["channel"], "timestamp": response["ts"]}


# TODO what about pagination?
def list_pins(client: Any, conversation_id: str):
    """Lists all pins for conversation."""
    return make_call(client, "pins.list", channel=conversation_id)


def add_pin(client: Any, conversation_id: str, timestamp: str):
    """Adds a pin to a conversation."""
    return make_call(client, "pins.add", channel=conversation_id, timestamp=timestamp)


def remove_pin(client: Any, conversation_id: str, timestamp: str):
    """Removed pin from conversation."""
    return make_call(client, "pins.remove", channel=conversation_id, timestamp=timestamp)


def message_filter(message):
    """Some messages are not useful, we filter them here."""
    if not message["text"]:  # sometimes for file upload there is no text only files
        return

    if message["type"] != "message":
        return

    if message.get("subtype"):
        return

    if message.get("bot_id"):
        return

    return message


def is_user(slack_user: str):
    """Returns true if it's a regular user, false if dispatch bot'."""
    return slack_user != SLACK_APP_USER_SLUG


def open_dialog_with_user(client: Any, trigger_id: str, dialog: dict):
    """Opens a dialog with a user."""
    return make_call(client, "dialog.open", trigger_id=trigger_id, dialog=dialog)


def open_view_for_user(client: Any, trigger_id: str, view: dict):
    """Opens a View for a user."""
    return make_call(client, "views.open", trigger_id=trigger_id, view=view)
