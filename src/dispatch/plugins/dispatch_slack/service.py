import time
import logging
import functools
import inspect
from pydantic import BaseModel
from pydantic.error_wrappers import ErrorWrapper, ValidationError

import slack_sdk
from slack_sdk.web.async_client import AsyncWebClient

from typing import Any, Dict, List, Optional

from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from dispatch.exceptions import NotFoundError
from dispatch.database.core import SessionLocal, sessionmaker, engine
from dispatch.conversation import service as conversation_service
from dispatch.organization import service as organization_service
from .config import SlackConversationConfiguration

log = logging.getLogger(__name__)


# we need a way to determine which organization to use for a given
# event, we use the unique channel id to determine which organization the
# event belongs to.
def get_organization_scope_from_channel_id(channel_id: str) -> SessionLocal:
    """Iterate all organizations looking for a relevant channel_id."""
    db_session = SessionLocal()
    organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]
    db_session.close()

    for slug in organization_slugs:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        scoped_db_session = sessionmaker(bind=schema_engine)()
        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=scoped_db_session, channel_id=channel_id
        )
        if conversation:
            return scoped_db_session

        scoped_db_session.close()


def get_organization_scope_from_slug(slug: str) -> SessionLocal:
    """Iterate all organizations looking for a matching slug."""
    db_session = SessionLocal()
    organization = organization_service.get_by_slug(db_session=db_session, slug=slug)
    db_session.close()

    if organization:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        return sessionmaker(bind=schema_engine)()

    raise ValidationError(
        [
            ErrorWrapper(
                NotFoundError(msg=f"Organization slug '{slug}' not found. Check your spelling."),
                loc="organization",
            )
        ],
        model=BaseModel,
    )


def get_default_organization_scope() -> str:
    """Iterate all organizations looking for matching organization."""
    db_session = SessionLocal()
    organization = organization_service.get_default(db_session=db_session)
    db_session.close()

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization.slug}",
        }
    )

    return sessionmaker(bind=schema_engine)()


def fullname(o):
    module = inspect.getmodule(o)
    return f"{module.__name__}.{o.__qualname__}"


def create_slack_client(config: SlackConversationConfiguration, run_async: bool = False):
    """Creates a Slack Web API client."""
    if not run_async:
        return slack_sdk.WebClient(token=config.api_bot_token.get_secret_value())
    return AsyncWebClient(token=config.api_bot_token.get_secret_value())


def resolve_user(client: Any, user_id: str):
    """Attempts to resolve a user object regardless if email, id, or prefix."""
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
SLACK_GET_ENDPOINTS = [
    "conversations.history",
    "conversations.info",
    "users.conversations",
    "users.info",
    "users.lookupByEmail",
    "users.profile.get",
]


@retry(stop=stop_after_attempt(5), retry=retry_if_exception_type(TryAgain))
def make_call(client: Any, endpoint: str, **kwargs):
    """Make an Slack client api call."""
    try:
        if endpoint in SLACK_GET_ENDPOINTS:
            response = client.api_call(endpoint, http_verb="GET", params=kwargs)
        else:
            response = client.api_call(endpoint, json=kwargs)
    except slack_sdk.errors.SlackApiError as e:
        log.error(f"SlackError. Response: {e.response} Endpoint: {endpoint} kwargs: {kwargs}")

        # NOTE we've seen some eventual consistency problems with channel creation
        if e.response["error"] == "channel_not_found":
            raise TryAgain

        # NOTE we've seen some eventual consistency problems after adding users to a channel
        if e.response["error"] == "user_not_in_channel":
            raise TryAgain

        # NOTE we've experienced a wide range of issues when Slack's performance is degraded
        if e.response["error"] == "fatal_error":
            # we wait 5 minutes before trying again, as performance issues
            # take time to troubleshoot and fix
            time.sleep(300)
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
    """Make an Slack client api call."""

    try:
        if endpoint in SLACK_GET_ENDPOINTS:
            response = await client.api_call(endpoint, http_verb="GET", params=kwargs)
        else:
            response = await client.api_call(endpoint, json=kwargs)
    except slack_sdk.errors.SlackApiError as e:
        log.error(f"SlackError. Response: {e.response} Endpoint: {endpoint} kwargs: {kwargs}")

        if e.response.headers.get("Retry-After"):
            wait = int(e.response.headers["Retry-After"])
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


# @functools.lru_cache()
async def get_user_info_by_id_async(client: Any, user_id: str):
    """Gets profile information about a user by id."""
    user_info = await make_call_async(client, "users.info", user=user_id)
    return user_info["user"]


@functools.lru_cache()
def get_user_info_by_email(client: Any, email: str):
    """Gets profile information about a user by email."""
    return make_call(client, "users.lookupByEmail", email=email)["user"]


async def get_user_info_by_email_async(client: Any, email: str):
    """Gets profile information about a user by email."""
    return (await make_call_async(client, "users.lookupByEmail", email=email))["user"]


@functools.lru_cache()
def get_user_profile_by_email(client: Any, email: str):
    """Gets extended profile information about a user by email."""
    user = make_call(client, "users.lookupByEmail", email=email)["user"]
    profile = make_call(client, "users.profile.get", user=user["id"])["profile"]
    profile["tz"] = user["tz"]
    return profile


async def get_user_profile_by_email_async(client: Any, email: str):
    """Gets extended profile information about a user by email."""
    user = (await make_call(client, "users.lookupByEmail", email=email))["user"]
    profile = (await make_call(client, "users.profile.get", user=user["id"]))["profile"]
    profile["tz"] = user["tz"]
    return profile


def get_user_email(client: Any, user_id: str):
    """Gets the user's email."""
    user_info = get_user_info_by_id(client, user_id)
    return user_info["profile"]["email"]


async def get_user_email_async(client: Any, user_id: str):
    """Gets the user's email."""
    user_info = await get_user_info_by_id_async(client, user_id)
    return user_info["profile"]["email"]


def get_user_username(client: Any, user_id: str):
    """Gets the user's username."""
    return get_user_email(client, user_id).split("@")[0]


def get_user_avatar_url(client: Any, email: str):
    """Gets the user's avatar url."""
    return get_user_info_by_email(client, email)["profile"]["image_512"]


async def get_user_avatar_url_async(client: Any, email: str):
    """Gets the user's avatar url."""
    return (await get_user_info_by_email_async(client, email))["profile"]["image_512"]


# note this will get slower over time, we might exclude archived to make it sane
def get_conversation_by_name(client: Any, name: str):
    """Fetches a conversation by name."""
    for c in list_conversations(client):
        if c["name"] == name:
            return c


def set_conversation_topic(client: Any, conversation_id: str, topic: str):
    """Sets the topic of the specified conversation."""
    return make_call(client, "conversations.setTopic", channel=conversation_id, topic=topic)


def create_conversation(client: Any, name: str, is_private: bool = False):
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


def archive_conversation(client: Any, conversation_id: str):
    """Archives an existing conversation."""
    return make_call(client, "conversations.archive", channel=conversation_id)


def unarchive_conversation(client: Any, conversation_id: str):
    """Unarchives an existing conversation."""
    try:
        return make_call(client, "conversations.unarchive", channel=conversation_id)
    except slack_sdk.errors.SlackApiError as e:
        # if the channel isn't archived thats okay
        if e.response["error"] != "not_archived":
            raise e


def conversation_archived(client: Any, conversation_id: str):
    """Returns whether a given conversation has been archived or not."""
    try:
        return make_call(client, "conversations.info", channel=conversation_id)["channel"][
            "is_archived"
        ]
    except slack_sdk.errors.SlackApiError as e:
        if e.response["error"] == "channel_not_found":
            return None
        else:
            raise e


def add_users_to_conversation(client: Any, conversation_id: str, user_ids: List[str]):
    """Add users to conversation."""
    # NOTE this will trigger a member_joined_channel event, which we will capture and run
    # the incident.incident_add_or_reactivate_participant_flow() as a result
    for c in chunks(user_ids, 30):  # NOTE api only allows 30 at a time.
        try:
            make_call(client, "conversations.invite", users=c, channel=conversation_id)
        except slack_sdk.errors.SlackApiError as e:
            # sometimes slack sends duplicate member_join events
            # that result in folks already existing in the channel.
            if e.response["error"] == "already_in_channel":
                pass


def send_message(
    client: Any,
    conversation_id: str,
    text: str = None,
    blocks: List[Dict] = None,
    persist: bool = False,
):
    """Sends a message to the given conversation."""
    response = make_call(
        client, "chat.postMessage", channel=conversation_id, text=text, blocks=blocks
    )

    if persist:
        add_pin(client, response["channel"], response["ts"])

    return {"id": response["channel"], "timestamp": response["ts"]}


def send_ephemeral_message(
    client: Any,
    conversation_id: str,
    user_id: str,
    text: str,
    blocks: Optional[List] = None,
    thread_ts: Optional[str] = None,
):
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


def add_pin(client: Any, conversation_id: str, timestamp: str):
    """Adds a pin to a conversation."""
    return make_call(client, "pins.add", channel=conversation_id, timestamp=timestamp)


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
