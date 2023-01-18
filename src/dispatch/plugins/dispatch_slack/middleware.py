import logging

from typing import Callable, Optional, NamedTuple

from aiocache import Cache
from slack_bolt.async_app import AsyncBoltContext, AsyncBoltRequest
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.orm.session import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.conversation import service as conversation_service
from dispatch.database.core import SessionLocal, engine, sessionmaker, refetch_db_session
from dispatch.decorators import async_timer
from dispatch.organization import service as organization_service
from dispatch.participant import service as participant_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.project import service as project_service
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from .exceptions import ContextError, RoleError, BotNotPresentError
from .models import SubjectMetadata


log = logging.getLogger(__file__)

cache = Cache()

Subject = NamedTuple("Subject", subject=SubjectMetadata, db_session=Session)


async def resolve_context_from_conversation(
    channel_id: str, message_ts: Optional[str] = None
) -> Optional[Subject]:
    """Attempts to resolve a conversation based on the channel id or message_ts."""

    organization_slugs = await cache.get("organization-slugs")

    if not organization_slugs:
        db_session = SessionLocal()
        organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]
        db_session.close()
        await cache.set("organization-slugs", organization_slugs)

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
            subject = SubjectMetadata(
                type="incident",
                id=conversation.incident_id,
                organization_slug=slug,
                project_id=conversation.incident.project_id,
            )
            return Subject(subject, db_session=scoped_db_session)

        scoped_db_session.close()


async def shortcut_context_middleware(context: AsyncBoltContext, next: Callable) -> None:
    """Attempts to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(channel_id=context.channel_id)})
    await next()


async def button_context_middleware(
    payload: dict, context: AsyncBoltContext, next: Callable
) -> None:
    """Attempt to determine the current context of the event."""
    try:
        subject_data = SubjectMetadata.parse_raw(payload["value"])
    except Exception:
        log.debug("Extracting context data from legacy template...")
        organization_slug, incident_id = payload["value"].split("-")
        subject_data = SubjectMetadata(
            organization_slug=organization_slug, id=incident_id, type="Incident"
        )

    context.update({"subject": subject_data})
    await next()


async def action_context_middleware(body: dict, context: AsyncBoltContext, next: Callable) -> None:
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(body["view"]["private_metadata"])})
    await next()


@async_timer
async def message_context_middleware(
    request: AsyncBoltRequest, context: AsyncBoltContext, next: Callable
) -> None:
    """Attemps to determine the current context of the event."""
    if is_bot(request):
        return await context.ack()

    if subject := await resolve_context_from_conversation(channel_id=context.channel_id):
        context.update(subject._asdict())
    else:
        raise ContextError("Unable to determine context for message.")

    await next()


@async_timer
async def restricted_command_middleware(
    context: AsyncBoltContext, db_session, user: DispatchUser, next: Callable, payload: dict
):
    """Rejects commands from unauthorized individuals."""
    allowed_roles = [ParticipantRoleType.incident_commander, ParticipantRoleType.scribe]
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )

    # if any required role is active, allow command
    for active_role in participant.active_roles:
        for allowed_role in allowed_roles:
            if active_role.role == allowed_role:
                return await next()

    raise RoleError(
        f"Participant does not have permission to run `{payload['command']}`. Roles with permission: {','.join([r.name for r in allowed_roles])}",
    )


# filter out member join bot events as the built in slack-bolt doesn't catch these events
# https://github.com/slackapi/bolt-python/blob/main/slack_bolt/middleware/ignoring_self_events/ignoring_self_events.py#L37
def is_bot(request: AsyncBoltRequest):
    auth_result = request.context.authorize_result
    user_id = request.context.user_id
    bot_id = request.body.get("event", {}).get("bot_id")
    body = request.body
    return (
        auth_result is not None
        and (
            (user_id is not None and user_id == auth_result.bot_user_id)
            or (bot_id is not None and bot_id == auth_result.bot_id)  # for bot_message events
        )
        and body.get("event") is not None
    )


@async_timer
async def user_middleware(
    body: dict,
    payload: dict,
    db_session: Session,
    client: AsyncWebClient,
    request: AsyncBoltRequest,
    context: AsyncBoltContext,
    next: Callable,
) -> None:
    """Attempts to determine the user making the request."""
    if is_bot(request):
        return await context.ack()

    user_id = None

    # for modals
    if body.get("user"):
        user_id = body["user"]["id"]

    # for messages
    if payload.get("user"):
        user_id = payload["user"]

    # for commands
    if payload.get("user_id"):
        user_id = payload["user_id"]

    if not user_id:
        raise ContextError("Unable to determine user from context.")

    email = await cache.get(user_id)
    if not email:
        email = (await client.users_info(user=user_id))["user"]["profile"]["email"]
        await cache.set(user_id, email)

    context["user"] = user_service.get_or_create(
        db_session=db_session,
        organization=context["subject"].organization_slug,
        user_in=UserRegister(email=email),
    )
    await next()


@async_timer
async def modal_submit_middleware(body: dict, context: AsyncBoltContext, next: Callable) -> None:
    """Parses view data into a reasonable data struct."""
    parsed_data = {}
    state_elem = body["view"].get("state")
    state_values = state_elem.get("values")

    for state in state_values:
        state_key_value_pair = state_values[state]

        for elem_key in state_key_value_pair:
            elem_key_value_pair = state_values[state][elem_key]

            if elem_key_value_pair.get("selected_option") and elem_key_value_pair.get(
                "selected_option"
            ).get("value"):
                parsed_data[state] = {
                    "name": elem_key_value_pair.get("selected_option").get("text").get("text"),
                    "value": elem_key_value_pair.get("selected_option").get("value"),
                }
            elif elem_key_value_pair.get("selected_user"):
                parsed_data[state] = {
                    "name": "user",
                    "value": elem_key_value_pair.get("selected_user"),
                }
            elif "selected_options" in elem_key_value_pair.keys():
                name = "No option selected"
                value = ""

                if elem_key_value_pair.get("selected_options"):
                    options = []
                    for selected in elem_key_value_pair["selected_options"]:
                        name = selected.get("text").get("text")
                        value = selected.get("value")
                        options.append({"name": name, "value": value})

                    parsed_data[state] = options
            elif elem_key_value_pair.get("selected_date"):
                parsed_data[state] = elem_key_value_pair.get("selected_date")
            else:
                parsed_data[state] = elem_key_value_pair.get("value")

    context["form_data"] = parsed_data
    await next()


# NOTE we don't need to handle cases because commands are not available in threads.
@async_timer
async def command_context_middleware(
    context: AsyncBoltContext, payload: dict, next: Callable
) -> None:
    if subject := await resolve_context_from_conversation(channel_id=context.channel_id):
        context.update(subject._asdict())
    else:
        raise ContextError(
            f"Sorry, I can't determine the correct context to run the command `{payload['command']}`. Are you running this command in an incident channel?"
        )
    await next()


@async_timer
async def db_middleware(context: AsyncBoltContext, next: Callable):
    if not context.get("subject"):
        slug = get_default_org_slug()
        context.update({"subject": SubjectMetadata(organization_slug=slug)})
    else:
        slug = context["subject"].organization_slug

    context["db_session"] = refetch_db_session(slug)
    await next()


@async_timer
async def subject_middleware(context: AsyncBoltContext, next: Callable):
    """"""
    if not context.get("subject"):
        slug = get_default_org_slug()
        context.update({"subject": SubjectMetadata(organization_slug=slug)})

    await next()


@async_timer
async def configuration_middleware(context: AsyncBoltContext, next: Callable):
    if context.get("config"):
        return await next()

    if not context.get("db_session"):
        slug = get_default_org_slug()
        db_session = refetch_db_session(slug)
    else:
        # handle_message_events() flow can contain a db_session in context
        db_session = context["db_session"]

    project_id = project_service.get_default(db_session=db_session).id

    plugin = await cache.get(project_id)
    if not plugin:
        plugin = plugin_service.get_active_instance(
            db_session=db_session,
            project_id=project_id,
            plugin_type="conversation",
        )
        await cache.set(project_id, plugin)

    context["config"] = plugin.configuration
    await next()


# This middleware has a dependency on configuration_middleware()
async def non_incident_command_middlware(
    client: AsyncWebClient,
    context: AsyncBoltContext,
    next: Callable,
):
    """Attempts to resolve a conversation based on the channel id or message_ts."""
    # We get the list of public and private conversations the Dispatch bot is a member of
    public_conversations = await dispatch_slack_service.get_public_conversations_by_user_id_async(
        client, context["config"].app_user_slug
    )
    private_conversations = await dispatch_slack_service.get_private_conversations_by_user_id_async(
        client, context["config"].app_user_slug
    )

    public_conversation_names = [c["name"] for c in public_conversations]
    private_conversation_names = [c["name"] for c in private_conversations]

    # We get the name of conversation where the command was run
    conversation_name = await dispatch_slack_service.get_conversation_name_by_id_async(
        client, context.channel_id
    )

    if (
        not conversation_name
        or conversation_name not in public_conversation_names + private_conversation_names  # noqa
    ):
        # We let the user know in which public conversations they can run the command
        context["conversations"] = public_conversations
        raise BotNotPresentError("User ran a command where the bot is not present.")

    await next()


def get_default_org_slug() -> str:
    db_session = SessionLocal()
    slug = organization_service.get_default(db_session=db_session).slug
    db_session.close()
    return slug
