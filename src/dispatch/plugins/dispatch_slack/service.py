import functools
import logging
import time

from typing import Dict, List, Optional, Union

from blockkit import Message, Section
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient
from slack_sdk.web.slack_response import SlackResponse

from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from .config import SlackConversationConfiguration

# List of Slack endpoints that require HTTP GET method
SLACK_GET_ENDPOINTS = [
    "conversations.history",
    "conversations.info",
    "users.conversations",
    "users.info",
    "users.lookupByEmail",
    "users.profile.get",
]

Conversation = dict[str, str]

log = logging.getLogger(__name__)


def create_slack_client(config: SlackConversationConfiguration) -> WebClient:
    """Creates a Slack Web API client."""
    return WebClient(token=config.api_bot_token.get_secret_value())


def resolve_user(client: WebClient, user_id: str) -> dict:
    """Attempts to resolve a user object regardless if email, id, or prefix is provided."""
    if "@" in user_id:
        return get_user_info_by_email(client, user_id)
    return {"id": user_id}


def chunks(ids, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(ids), n):
        yield ids[i : i + n]


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


def handle_slack_error(exception: SlackApiError, endpoint: str, kwargs: dict):
    message = (
        f"SlackAPIError. Response: {exception.response}. Endpoint: {endpoint}. Kwargs: {kwargs}"
    )
    error = exception.response["error"]

    if error in {"channel_not_found", "user_not_in_channel"}:
        # NOTE we've seen some consistency problems with channel creation, adding users to channels or messaging them.
        log.warn(message)
        raise TryAgain from None
    elif error == "fatal_error":
        # NOTE we've experienced a wide range of issues when Slack's performance is degraded
        log.error(message)
        time.sleep(300)
        raise TryAgain from None
    elif exception.response.headers.get("Retry-After"):
        wait = int(exception.response.headers["Retry-After"])
        log.info(f"SlackError: Rate limit hit. Waiting {wait} seconds.")
        time.sleep(wait)
        raise TryAgain from None
    else:
        raise exception


@retry(stop=stop_after_attempt(5), retry=retry_if_exception_type(TryAgain))
def make_call(client: WebClient, endpoint: str, **kwargs) -> SlackResponse:
    """Makes a Slack client API call."""
    try:
        if endpoint in SLACK_GET_ENDPOINTS:
            response = client.api_call(endpoint, http_verb="GET", params=kwargs)
        else:
            response = client.api_call(endpoint, json=kwargs)
    except SlackApiError as e:
        handle_slack_error(e, endpoint, kwargs)
    return response


@paginated("channels")
def list_conversations(client: WebClient, **kwargs) -> SlackResponse:
    return make_call(client, "conversations.list", types="private_channel", **kwargs)


def list_conversation_messages(client: WebClient, conversation_id: str, **kwargs) -> SlackResponse:
    """Returns a list of conversation messages."""
    return make_call(client, "conversations.history", channel=conversation_id, **kwargs)


@functools.lru_cache()
def get_user_info_by_id(client: WebClient, user_id: str) -> SlackResponse:
    """Gets profile information about a user by id."""
    return make_call(client, "users.info", user=user_id)["user"]


@functools.lru_cache()
def get_user_info_by_email(client: WebClient, email: str) -> SlackResponse:
    """Gets profile information about a user by email."""
    return make_call(client, "users.lookupByEmail", email=email)["user"]


@functools.lru_cache()
def get_user_profile_by_email(client: WebClient, email: str) -> SlackResponse:
    """Gets extended profile information about a user by email."""
    user = make_call(client, "users.lookupByEmail", email=email)["user"]
    profile = make_call(client, "users.profile.get", user=user["id"])["profile"]
    profile["tz"] = user["tz"]
    return profile


def get_user_email(client: WebClient, user_id: str) -> str:
    """Gets the user's email."""
    user_info = get_user_info_by_id(client, user_id)
    return user_info["profile"]["email"]


def get_user_avatar_url(client: WebClient, email: str) -> str:
    """Gets the user's avatar url."""
    return get_user_info_by_email(client, email)["profile"]["image_512"]


def get_conversations_by_user_id(client: WebClient, user_id: str, type: str) -> List[Conversation]:
    result = make_call(
        client,
        "users.conversations",
        user=user_id,
        types=f"{type}_channel",
        exclude_archived="true",
    )

    conversations = []
    for channel in result["channels"]:
        conversations.append({k: v for (k, v) in channel.items() if k == "id" or k == "name"})

    return conversations


# note this will get slower over time, we might exclude archived to make it sane
def get_conversation_by_name(client: WebClient, name: str) -> Conversation:
    """Fetches a conversation by name."""
    for c in list_conversations(client):
        if c["name"] == name:
            return c


def get_conversation_name_by_id(client: WebClient, conversation_id: str) -> SlackResponse:
    """Fetches a conversation by id and returns its name."""
    try:
        return make_call(client, "conversations.info", channel=conversation_id)["channel"]["name"]
    except SlackApiError as e:
        if e.response["error"] == "channel_not_found":
            return None
        else:
            raise e


def set_conversation_topic(client: WebClient, conversation_id: str, topic: str) -> SlackResponse:
    """Sets the topic of the specified conversation."""
    return make_call(client, "conversations.setTopic", channel=conversation_id, topic=topic)


def add_conversation_bookmark(
    client: WebClient, conversation_id: str, weblink: str, title: str
) -> SlackResponse:
    """Adds a bookmark for the specified conversation."""
    return make_call(
        client,
        "bookmarks.add",
        channel_id=conversation_id,
        title=title,
        type="link",
        link=weblink,
    )


def create_conversation(client: WebClient, name: str, is_private: bool = False) -> dict:
    """Make a new Slack conversation."""
    response = make_call(
        client,
        "conversations.create",
        name=name.lower(),  # slack disallows upperCase
        is_group=is_private,
        is_private=is_private,
    )["channel"]

    return {
        "id": response["id"],
        "name": response["name"],
        "weblink": f"https://slack.com/app_redirect?channel={response['id']}",
    }


def archive_conversation(client: WebClient, conversation_id: str) -> SlackResponse:
    """Archives an existing conversation."""
    return make_call(client, "conversations.archive", channel=conversation_id)


def unarchive_conversation(client: WebClient, conversation_id: str) -> SlackResponse:
    """Unarchives an existing conversation."""
    try:
        return make_call(client, "conversations.unarchive", channel=conversation_id)
    except SlackApiError as e:
        # if the channel isn't archived thats okay
        if e.response["error"] != "not_archived":
            raise e


def rename_conversation(client: WebClient, conversation_id: str, name: str) -> SlackResponse:
    """Renames an existing conversation."""
    return make_call(client, "conversations.rename", channel=conversation_id, name=name)


def conversation_archived(client: WebClient, conversation_id: str):
    """Returns whether a given conversation has been archived or not."""
    try:
        return make_call(client, "conversations.info", channel=conversation_id)["channel"][
            "is_archived"
        ]
    except SlackApiError as e:
        if e.response["error"] == "channel_not_found":
            return None
        else:
            raise e


def add_users_to_conversation_thread(
    client: WebClient, conversation_id: str, thread_id, user_ids: List[str]
):
    """Adds user to a threaded conversation."""
    users = [f"<@{user_id}>" for user_id in user_ids]
    if users:
        blocks = Message(
            blocks=[
                Section(text="Looping in individuals to help resolve this case...", fields=users)
            ]
        ).build()["blocks"]
        send_message(client=client, conversation_id=conversation_id, blocks=blocks, ts=thread_id)


def add_users_to_conversation(client: WebClient, conversation_id: str, user_ids: List[str]):
    """Add users to conversation."""
    # NOTE this will trigger a member_joined_channel event, which we will capture and run
    # the incident.incident_add_or_reactivate_participant_flow() as a result
    for c in chunks(user_ids, 30):  # NOTE api only allows 30 at a time.
        try:
            make_call(client, "conversations.invite", users=c, channel=conversation_id)
        except SlackApiError as e:
            # sometimes slack sends duplicate member_join events
            # that result in folks already existing in the channel.
            if e.response["error"] == "already_in_channel":
                pass


def send_message(
    client: WebClient,
    conversation_id: str,
    text: str = None,
    ts: str = None,
    blocks: List[Dict] = None,
    persist: bool = False,
) -> dict:
    """Sends a message to the given conversation."""
    response = make_call(
        client, "chat.postMessage", channel=conversation_id, text=text, thread_ts=ts, blocks=blocks
    )

    if persist:
        add_pin(client, response["channel"], response["ts"])

    return {
        "id": response["channel"],
        "timestamp": response["ts"],
        "weblink": f"https://slack.com/app_redirect?channel={response['id']}",  # TODO should we fetch the permalink?
    }


def update_message(
    client: WebClient,
    conversation_id: str,
    text: str = None,
    ts: str = None,
    blocks: List[Dict] = None,
) -> dict:
    """Updates a message for the given conversation."""
    response = make_call(
        client, "chat.update", channel=conversation_id, text=text, ts=ts, blocks=blocks
    )

    return {
        "id": response["channel"],
        "timestamp": response["ts"],
        "weblink": f"https://slack.com/app_redirect?channel={response['id']}",  # TODO should we fetch the permalink?
    }


def send_ephemeral_message(
    client: WebClient,
    conversation_id: str,
    user_id: str,
    text: str,
    blocks: Optional[List] = None,
    thread_ts: Optional[str] = None,
) -> dict:
    """Sends an ephemeral message to a user in a channel."""
    if thread_ts:
        response = make_call(
            client,
            "chat.postEphemeral",
            channel=conversation_id,
            user=user_id,
            text=text,
            thread_ts=thread_ts,
            blocks=blocks,
        )
    else:
        response = make_call(
            client,
            "chat.postEphemeral",
            channel=conversation_id,
            user=user_id,
            text=text,
            blocks=blocks,
        )

    return {"id": response["channel"], "timestamp": response["ts"]}


def add_pin(client: WebClient, conversation_id: str, timestamp: str) -> SlackResponse:
    """Adds a pin to a conversation."""
    return make_call(client, "pins.add", channel=conversation_id, timestamp=timestamp)


def message_filter(message) -> Union[str, None]:
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


def is_user(config: SlackConversationConfiguration, user_id: str) -> bool:
    """Returns true if it's a regular user, false if Dispatch or Slackbot bot'."""
    return user_id != config.app_user_slug and user_id != "USLACKBOT"
