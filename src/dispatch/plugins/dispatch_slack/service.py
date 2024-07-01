from datetime import datetime
import functools
import heapq
import logging
from requests import Timeout

from blockkit import Message, Section
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient
from slack_sdk.web.slack_response import SlackResponse
from tenacity import retry, retry_if_exception, wait_exponential, stop_after_attempt, RetryCallState

from typing import Dict, List, Optional

from .config import SlackConversationConfiguration
from .enums import SlackAPIErrorCode, SlackAPIGetEndpoints, SlackAPIPostEndpoints


Conversation = dict[str, str]

log = logging.getLogger(__name__)


class SlackRetryException(Exception):
    def __init__(self, wait_time: int | None = None):
        self.wait_time = wait_time
        if wait_time:
            super().__init__(f"Retrying slack call in {wait_time} seconds.")
        else:
            super().__init__("Retrying slack call.")

    def get_wait_time(self) -> int:
        return self.wait_time


def slack_wait_strategy(retry_state: RetryCallState) -> float | int:
    """Determines the wait time for the Slack retry strategy"""
    exc = retry_state.outcome.exception()

    if hasattr(exc, 'get_wait_time') and callable(exc.get_wait_time):
        return exc.get_wait_time()

    # Fallback to exponential backoff if no custom wait time is specified
    return wait_exponential(multiplier=1, min=1, max=60)(retry_state)


def create_slack_client(config: SlackConversationConfiguration) -> WebClient:
    """Creates a Slack Web API client."""
    return WebClient(token=config.api_bot_token.get_secret_value())


def resolve_user(client: WebClient, user_id: str) -> dict:
    """Attempts to resolve a user object regardless if email, id, or prefix is provided."""
    if "@" in user_id:
        return get_user_info_by_email(client, user_id)
    return {"id": user_id}


def emails_to_user_ids(client: WebClient, participants: list[str]) -> list[str]:
    """
    Resolves a list of email addresses to Slack user IDs.

    This function takes a list of email addresses and attempts to resolve them to Slack user IDs.
    If a user cannot be found for a given email address, it logs a warning and continues with the next email.
    If an error other than a user not found occurs, it logs the exception.

    Args:
        client (WebClient): A Slack WebClient object used to interact with the Slack API.
        participants (list[str]): A list of participant email addresses to resolve.

    Returns:
        list[str]: A list of resolved user IDs.

    Raises:
        SlackApiError: If an error other than a user not found occurs.

    Example:
        >>> from slack_sdk import WebClient
        >>> client = WebClient(token="your-slack-token")
        >>> emails = ["user1@example.com", "user2@example.com"]
        >>> user_ids = emails_to_user_ids(client, emails)
        >>> print(user_ids)
        ["U01ABCDE1", "U01ABCDE2"]
    """
    user_ids = []

    for participant in set(participants):
        try:
            user_id = resolve_user(client, participant)["id"]
        except SlackApiError as e:
            msg = f"Unable to resolve Slack participant {participant}: {e}"

            if e.response["error"] == SlackAPIErrorCode.USERS_NOT_FOUND:
                log.warning(msg)
                continue
            else:
                log.exception(msg)
                continue
        else:
            user_ids.append(user_id)

    return user_ids


def chunks(ids, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(ids), n):
        yield ids[i : i + n]


@retry(stop=stop_after_attempt(5), retry=retry_if_exception(SlackRetryException), wait=slack_wait_strategy)
def make_call(client: WebClient, endpoint: str, **kwargs) -> SlackResponse:
    """Makes a call to the Slack API.

    This function attempts to be resilient to common Slack API errors, such as rate limiting and fatal errors.
    Rate limiting will be retried after the specified wait time (as returned by slack), and fatal errors will be raised as exceptions.

    Args:
        client (WebClient): Slack web client.
        endpoint (str): The Slack API endpoint to call.

    Raises:
        SlackRetryException: If the call fails and should be retried.

    Returns:
        SlackResponse: The response from the Slack API.
    """
    try:
        if endpoint in set(SlackAPIGetEndpoints):
            return client.api_call(endpoint, http_verb="GET", params=kwargs)
        return client.api_call(endpoint, json=kwargs)
    except SlackApiError as exception:
        message = (
            f"SlackAPIError. Response: {exception.response}. Endpoint: {endpoint}. Kwargs: {kwargs}"
        )

        error = exception.response["error"]
        if error == SlackAPIErrorCode.FATAL_ERROR:
            log.warn(message)
            raise SlackRetryException from None

        elif exception.response.headers.get("Retry-After"):
            wait = int(exception.response.headers["Retry-After"])
            log.warn(f"SlackError: Rate limit hit. Waiting {wait} seconds.")
            raise SlackRetryException(wait) from None

        # fatal error, don't retry
        raise exception
    except (TimeoutError, Timeout) as exception:
        log.warn(f"{type(exception).__name__} error {exception} for slack. Endpoint: {endpoint}. Kwargs: {kwargs}")
        raise SlackRetryException from None


def list_conversation_messages(client: WebClient, conversation_id: str, **kwargs) -> SlackResponse:
    """Returns a list of conversation messages."""
    return make_call(
        client, SlackAPIGetEndpoints.conversations_history, channel=conversation_id, **kwargs
    )


@functools.lru_cache()
def get_domain(client: WebClient) -> str:
    """Gets the team's Slack domain."""
    return make_call(client, SlackAPIGetEndpoints.team_info)["team"]["domain"]


@functools.lru_cache()
def get_user_info_by_id(client: WebClient, user_id: str) -> dict:
    """Gets profile information about a user by id."""
    return make_call(client, SlackAPIGetEndpoints.users_info, user=user_id)["user"]


@functools.lru_cache()
def get_user_info_by_email(client: WebClient, email: str) -> dict:
    """Gets profile information about a user by email."""
    return make_call(client, SlackAPIGetEndpoints.users_lookup_by_email, email=email)["user"]


@functools.lru_cache()
def does_user_exist(client: WebClient, email: str) -> bool:
    """Checks if a user exists in the Slack workspace by their email."""
    try:
        get_user_info_by_email(client, email)
        return True
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.USERS_NOT_FOUND:
            return False
        else:
            raise


@functools.lru_cache()
def get_user_profile_by_id(client: WebClient, user_id: str) -> dict:
    """Gets profile information about a user by id."""
    return make_call(client, SlackAPIGetEndpoints.users_profile_get, user_id=user_id)["profile"]


@functools.lru_cache()
def get_user_profile_by_email(client: WebClient, email: str) -> SlackResponse:
    """Gets extended profile information about a user by email."""
    user = get_user_info_by_email(client, email)
    profile = get_user_profile_by_id(client, user["id"])
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
        SlackAPIGetEndpoints.users_conversations,
        user=user_id,
        types=f"{type}_channel",
        exclude_archived="true",
    )

    conversations = []
    for channel in result["channels"]:
        conversations.append({k: v for (k, v) in channel.items() if k == "id" or k == "name"})

    return conversations


# note this will get slower over time, we might exclude archived to make it sane
def get_conversation_name_by_id(client: WebClient, conversation_id: str) -> SlackResponse:
    """Fetches a conversation by id and returns its name."""
    try:
        return make_call(client, SlackAPIGetEndpoints.conversations_info, channel=conversation_id)[
            "channel"
        ]["name"]
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.CHANNEL_NOT_FOUND:
            return None
        else:
            raise e


def set_conversation_topic(client: WebClient, conversation_id: str, topic: str) -> SlackResponse:
    """Sets the topic of the specified conversation."""
    return make_call(
        client, SlackAPIPostEndpoints.conversations_set_topic, channel=conversation_id, topic=topic
    )


def set_conversation_description(client: WebClient, conversation_id: str, description: str) -> SlackResponse:
    """Sets the topic of the specified conversation."""
    return make_call(
        client, SlackAPIPostEndpoints.conversations_set_purpose, channel=conversation_id, purpose=description
    )


def add_conversation_bookmark(
    client: WebClient, conversation_id: str, weblink: str, title: str
) -> SlackResponse:
    """Adds a bookmark for the specified conversation."""
    return make_call(
        client,
        SlackAPIPostEndpoints.bookmarks_add,
        channel_id=conversation_id,
        title=title,
        type="link",
        link=weblink,
    )


def create_conversation(client: WebClient, name: str, is_private: bool = False) -> dict:
    """Make a new Slack conversation."""
    response = make_call(
        client,
        SlackAPIPostEndpoints.conversations_create,
        name=name.lower(),  # slack disallows upperCase
        is_group=is_private,
        is_private=is_private,
    )["channel"]

    return {
        "id": response["id"],
        "name": response["name"],
        "weblink": f"https://{get_domain(client)}.slack.com/app_redirect?channel={response['id']}",
    }


def archive_conversation(client: WebClient, conversation_id: str) -> SlackResponse:
    """Archives an existing conversation."""
    return make_call(client, SlackAPIPostEndpoints.conversations_archive, channel=conversation_id)


def unarchive_conversation(client: WebClient, conversation_id: str) -> SlackResponse:
    """Unarchives an existing conversation."""
    try:
        return make_call(
            client, SlackAPIPostEndpoints.conversations_unarchive, channel=conversation_id
        )
    except SlackApiError as e:
        # if the channel isn't archived thats okay
        if e.response["error"] != SlackAPIErrorCode.CHANNEL_NOT_ARCHIVED:
            raise e


def rename_conversation(client: WebClient, conversation_id: str, name: str) -> SlackResponse:
    """Renames an existing conversation."""
    return make_call(
        client, SlackAPIPostEndpoints.conversations_rename, channel=conversation_id, name=name.lower()
    )


def conversation_archived(client: WebClient, conversation_id: str) -> bool | None:
    """Returns whether a given conversation has been archived or not."""
    try:
        return make_call(client, SlackAPIGetEndpoints.conversations_info, channel=conversation_id)[
            "channel"
        ]["is_archived"]
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.CHANNEL_NOT_FOUND:
            return None
        else:
            raise e


def add_users_to_conversation_thread(
    client: WebClient,
    conversation_id: str,
    thread_id,
    user_ids: list[str],
) -> None:
    """Adds user to a threaded conversation."""

    users = [f"<@{user_id}>" for user_id in user_ids]
    if users:
        # @'ing them isn't enough if they aren't already in the channel
        add_users_to_conversation(client=client, conversation_id=conversation_id, user_ids=user_ids)
        blocks = Message(
            blocks=[
                Section(
                    text="Adding the following individuals to help resolve this case:", fields=users
                )
            ]
        ).build()["blocks"]
        send_message(client=client, conversation_id=conversation_id, blocks=blocks, ts=thread_id)


def add_users_to_conversation(client: WebClient, conversation_id: str, user_ids: List[str]) -> None:
    """Add users to conversation."""
    # NOTE this will trigger a member_joined_channel event, which we will capture and run
    # the incident.incident_add_or_reactivate_participant_flow() as a result
    for c in chunks(user_ids, 30):  # NOTE api only allows 30 at a time.
        try:
            make_call(
                client, SlackAPIPostEndpoints.conversations_invite, users=c, channel=conversation_id
            )
        except SlackApiError as e:
            # sometimes slack sends duplicate member_join events
            # that result in folks already existing in the channel.
            if e.response["error"] == SlackAPIErrorCode.USER_IN_CHANNEL:
                pass


def get_message_permalink(client: WebClient, conversation_id: str, ts: str) -> str:
    return make_call(
        client,
        SlackAPIGetEndpoints.chat_permalink,
        channel=conversation_id,
        message_ts=ts,
    )["permalink"]


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
        client,
        SlackAPIPostEndpoints.chat_post_message,
        channel=conversation_id,
        text=text,
        thread_ts=ts,
        blocks=blocks,
    )

    if persist:
        add_pin(client, response["channel"], response["ts"])

    return {
        "id": response["channel"],
        "timestamp": response["ts"],
        "weblink": get_message_permalink(client, response["channel"], response["ts"]),
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
        client,
        SlackAPIPostEndpoints.chat_update,
        channel=conversation_id,
        text=text,
        ts=ts,
        blocks=blocks,
    )

    return {
        "id": response["channel"],
        "timestamp": response["ts"],
        "weblink": get_message_permalink(client, response["channel"], response["ts"]),
    }


def send_ephemeral_message(
    client: WebClient,
    conversation_id: str,
    user_id: str,
    text: str,
    blocks: Optional[List] = None,
    thread_ts: Optional[str] = None,
) -> dict:
    """Sends an ephemeral message to a user in a channel or thread."""
    if thread_ts:
        response = make_call(
            client,
            SlackAPIPostEndpoints.chat_post_ephemeral,
            channel=conversation_id,
            user=user_id,
            text=text,
            thread_ts=thread_ts,
            blocks=blocks,
        )
    else:
        response = make_call(
            client,
            SlackAPIPostEndpoints.chat_post_ephemeral,
            channel=conversation_id,
            user=user_id,
            text=text,
            blocks=blocks,
        )

    return {"id": response["channel"], "timestamp": response["ts"]}


def add_pin(client: WebClient, conversation_id: str, timestamp: str) -> SlackResponse:
    """Adds a pin to a conversation."""
    return make_call(
        client, SlackAPIPostEndpoints.pins_add, channel=conversation_id, timestamp=timestamp
    )


def is_user(config: SlackConversationConfiguration, user_id: str) -> bool:
    """Returns true if it's a regular user, false if Dispatch or Slackbot bot."""
    return user_id != config.app_user_slug and user_id != "USLACKBOT"


def get_thread_activity(
    client: WebClient, conversation_id: str, ts: str, oldest: str = "0"
) -> List:
    """Gets all messages for a given Slack thread.

    Returns:
        A sorted list of tuples (utc_dt, user_id) of each thread reply.
    """
    result = []
    cursor = None
    while True:
        response = make_call(
            client,
            SlackAPIGetEndpoints.conversations_replies,
            channel=conversation_id,
            ts=ts,
            cursor=cursor,
            oldest=oldest,
        )
        if not response["ok"] or "messages" not in response:
            break

        for message in response["messages"]:
            if "bot_id" in message:
                continue

            # Resolves users for messages.
            if "user" in message:
                user_id = resolve_user(client, message["user"])["id"]
                heapq.heappush(result, (datetime.utcfromtimestamp(float(message["ts"])), user_id))

        if not response["has_more"]:
            break
        cursor = response["response_metadata"]["next_cursor"]

    return heapq.nsmallest(len(result), result)


def get_channel_activity(client: WebClient, conversation_id: str, oldest: str = "0") -> List:
    """Gets all top-level messages for a given Slack channel.

    Returns:
        A sorted list of tuples (utc_dt, user_id) of each message in the channel.
    """
    result = []
    cursor = None
    while True:
        response = make_call(
            client,
            SlackAPIGetEndpoints.conversations_history,
            channel=conversation_id,
            cursor=cursor,
            oldest=oldest,
        )

        if not response["ok"] or "messages" not in response:
            break

        for message in response["messages"]:
            if "bot_id" in message:
                continue

            # Resolves users for messages.
            if "user" in message:
                user_id = resolve_user(client, message["user"])["id"]
                heapq.heappush(result, (datetime.utcfromtimestamp(float(message["ts"])), user_id))

        if not response["has_more"]:
            break
        cursor = response["response_metadata"]["next_cursor"]

    return heapq.nsmallest(len(result), result)
