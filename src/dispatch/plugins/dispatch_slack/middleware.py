import logging
import json
from typing import Callable, NamedTuple, Optional

from slack_bolt import BoltContext, BoltRequest
from slack_sdk.web import WebClient
from sqlalchemy.orm.session import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.conversation import service as conversation_service
from dispatch.database.core import get_session, get_organization_session, refetch_db_session
from dispatch.decorators import timer
from dispatch.enums import SubjectNames
from dispatch.organization import service as organization_service
from dispatch.participant import service as participant_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack.models import SlackCommandPayload
from dispatch.plugins.dispatch_slack.exceptions import CommandError
from dispatch.project import service as project_service

from .exceptions import ContextError, RoleError
from .models import (
    EngagementMetadata,
    SubjectMetadata,
    FormMetadata,
    IncidentSubjects,
    CaseSubjects,
)

log = logging.getLogger(__file__)


Subject = NamedTuple("Subject", subject=SubjectMetadata, db_session=Session)


@timer
def resolve_context_from_conversation(channel_id: str, thread_id: str = None) -> Optional[Subject]:
    """Attempts to resolve a conversation based on the channel id and thread_id."""
    organization_slugs = []
    with get_session() as db_session:
        organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]

    for slug in organization_slugs:
        with get_organization_session(slug) as scoped_db_session:
            conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
                db_session=scoped_db_session, channel_id=channel_id, thread_id=thread_id
            )

            if conversation:
                if conversation.incident:
                    subject = SubjectMetadata(
                        type=IncidentSubjects.incident,
                        id=conversation.incident_id,
                        organization_slug=slug,
                        project_id=conversation.incident.project_id,
                    )
                else:
                    subject = SubjectMetadata(
                        type=CaseSubjects.case,
                        id=conversation.case_id,
                        organization_slug=slug,
                        project_id=conversation.case.project_id,
                    )
                return Subject(subject, db_session=scoped_db_session)


def select_context_middleware(payload: dict, context: BoltContext, next: Callable) -> None:
    """Attempt to determine the current context of the selection."""
    if not payload.get("selected_option"):
        return next()

    organization_slug, incident_id, *_ = payload["selected_option"]["value"].split("-")
    subject_data = SubjectMetadata(
        organization_slug=organization_slug, id=incident_id, type="Incident"
    )

    context.update({"subject": subject_data})
    next()


def shortcut_context_middleware(context: BoltContext, next: Callable) -> None:
    """Attempts to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(channel_id=context.channel_id)})
    next()


def button_context_middleware(payload: dict, context: BoltContext, next: Callable) -> None:
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
    next()


def engagement_button_context_middleware(
    payload: dict, context: BoltContext, next: Callable
) -> None:
    """Attempt to determine the current context of the event. Payload is populated by
    the `create_signal_engagement_message` function in `dispatch_slack/case/messages.py`.

    Example Payload:
        {
            'action_id': 'signal-engagement-approve',
            'block_id': 'Zqr+v',
            'text': {
                'type': 'plain_text',
                'text': 'Approve',
                'emoji': True
            },
            'value': '{
                "id": "5362",
                "type": "case",
                "organization_slug":
                "default", "project_id": "1",
                "channel_id": "C04KJP0BLUT",
                "signal_instance_id": "21077511-c53c-4d10-a2eb-998a5c972e09",
                "engagement_id": 5,
                "user": "wshel@netflix.com"
            }',
            'style': 'primary',
            'type': 'button', 'action_ts': '1689348164.534992'
        }
    """
    subject_data = EngagementMetadata.parse_raw(payload["value"])
    context.update({"subject": subject_data})
    next()


def action_context_middleware(body: dict, context: BoltContext, next: Callable) -> None:
    """Attempt to determine the current context of the event."""
    private_metadata = json.loads(body["view"]["private_metadata"])
    if private_metadata.get("form_data"):
        context.update({"subject": FormMetadata(**private_metadata)})
    else:
        context.update({"subject": SubjectMetadata(**private_metadata)})
    next()


def message_context_middleware(
    request: BoltRequest, payload: dict, context: BoltContext, next: Callable
) -> None:
    """Attempts to determine the current context of the event."""
    if is_bot(request):
        return context.ack()

    if subject := resolve_context_from_conversation(
        channel_id=context.channel_id, thread_id=payload.get("thread_ts")
    ):
        context.update(subject._asdict())
    else:
        raise ContextError("Unable to determine context for message.")

    next()


# TODO should we support reactions for cases?
def reaction_context_middleware(context: BoltContext, next: Callable) -> None:
    """Attempts to determine the current context of a reaction event."""
    if subject := resolve_context_from_conversation(channel_id=context.channel_id):
        context.update(subject._asdict())
    else:
        raise ContextError("Unable to determine context for reaction.")
    next()


@timer
def restricted_command_middleware(
    context: BoltContext, db_session, user: DispatchUser, next: Callable, payload: dict
):
    """Rejects commands from unauthorized individuals."""
    allowed_roles = [ParticipantRoleType.incident_commander, ParticipantRoleType.scribe]
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )
    if not participant:
        raise RoleError(
            f"User is not a participant in the incident and does not have permission to run `{payload['command']}`."
        )

    # if any required role is active, allow command
    for active_role in participant.active_roles:
        for allowed_role in allowed_roles:
            if active_role.role == allowed_role:
                return next()

    raise RoleError(
        f"Participant does not have permission to run `{payload['command']}`. Roles with permission: {','.join([r.name for r in allowed_roles])}",
    )


# filter out member join bot events as the built in slack-bolt doesn't catch these events
# https://github.com/slackapi/bolt-python/blob/main/slack_bolt/middleware/ignoring_self_events/ignoring_self_events.py#L37
def is_bot(request: BoltRequest) -> bool:
    body = request.body
    user = body.get("event", {}).get("user")
    if user == "USLACKBOT":
        return True

    auth_result = request.context.authorize_result
    user_id = request.context.user_id
    bot_id = body.get("event", {}).get("bot_id")

    return (
        auth_result is not None
        and (  # noqa
            (user_id is not None and user_id == auth_result.bot_user_id)
            or (  # noqa
                bot_id is not None and bot_id == auth_result.bot_id  # for bot_message events
            )
        )
        and body.get("event") is not None  # noqa
    )


@timer
def user_middleware(
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    request: BoltRequest,
    next: Callable,
    payload: dict,
) -> None:
    """Attempts to determine the user making the request."""
    if is_bot(request):
        return context.ack()

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

    context["user_id"] = user_id

    if not db_session:
        slug = (
            context["subject"].organization_slug
            if context["subject"].organization_slug
            else get_default_org_slug()
        )
        db_session = refetch_db_session(slug)

    participant = None
    # in the case of creating new incidents or cases we don't have a subject yet
    if context["subject"].id:
        if context["subject"].type == "incident":
            participant = participant_service.get_by_incident_id_and_conversation_id(
                db_session=db_session,
                incident_id=context["subject"].id,
                user_conversation_id=user_id,
            )
        else:
            participant = participant_service.get_by_case_id_and_conversation_id(
                db_session=db_session, case_id=context["subject"].id, user_conversation_id=user_id
            )

    user = None
    if participant:
        user = user_service.get_or_create(
            db_session=db_session,
            organization=context["subject"].organization_slug,
            user_in=UserRegister(email=participant.individual.email),
        )
    else:
        user_info = client.users_info(user=user_id).get("user", {})

        if user_info.get("is_bot", False):
            return context.ack()

        email = user_info.get("profile", {}).get("email")

        if not email:
            raise ContextError("Unable to get user email address.")

        user = user_service.get_or_create(
            db_session=db_session,
            organization=context["subject"].organization_slug,
            user_in=UserRegister(email=email),
        )

    if not user:
        raise ContextError("Unable to determine user from context.")

    context["user"] = user
    return next()


def modal_submit_middleware(body: dict, context: BoltContext, next: Callable) -> None:
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
    next()


# NOTE we don't need to handle cases because commands are not available in threads.
def command_context_middleware(
    context: BoltContext,
    payload: SlackCommandPayload,
    next: Callable,
    expected_subject: SubjectNames = SubjectNames.INCIDENT,
) -> None:
    subject = resolve_context_from_conversation(channel_id=context.channel_id)
    if not subject:
        raise ContextError(
            f"Sorry, we were unable to determine the correct context to run the command `{payload['command']}`. Are you running this command in a {expected_subject.lower()} channel?"
        )

    if not subject.subject.type == expected_subject.lower():
        raise CommandError(
            f"This command is only available with {expected_subject}s. {payload.get('channel_name', 'This channel')} is a {subject.subject.type}."
        )

    context.update(subject._asdict())
    next()


def db_middleware(context: BoltContext, next: Callable):
    if not context.get("subject"):
        slug = get_default_org_slug()
        context.update({"subject": SubjectMetadata(organization_slug=slug)})
    else:
        slug = context["subject"].organization_slug

    with get_organization_session(slug) as db_session:
        context["db_session"] = db_session
        next()


def subject_middleware(context: BoltContext, next: Callable):
    """"""
    if not context.get("subject"):
        slug = get_default_org_slug()
        context.update({"subject": SubjectMetadata(organization_slug=slug)})
    next()


def configuration_middleware(context: BoltContext, next: Callable):
    if context.get("config"):
        return next()

    if not context.get("db_session"):
        slug = get_default_org_slug()
        db_session = refetch_db_session(slug)
        context["db_session"] = db_session
    else:
        # handle_message_events() flow can contain a db_session in context
        db_session = context["db_session"]

    project_id = project_service.get_default(db_session=db_session).id

    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=project_id,
        plugin_type="conversation",
    )

    context["config"] = plugin.configuration
    next()


def get_default_org_slug() -> str:
    with get_session() as db_session:
        slug = organization_service.get_default(db_session=db_session).slug
    return slug
