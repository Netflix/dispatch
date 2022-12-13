from typing import Optional

from sqlalchemy.orm.session import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser
from dispatch.conversation import service as conversation_service
from dispatch.conversation.models import Conversation
from dispatch.database.core import SessionLocal, engine, sessionmaker
from dispatch.organization import service as organization_service
from dispatch.participant import service as participant_service
from dispatch.participant_role.enums import ParticipantRoleType

from .models import SubjectMetadata


def resolve_conversation_from_context(
    channel_id: str, message_ts: str = None
) -> Optional[Conversation]:
    """Attempts to resolve a conversation based on the channel id or message_ts."""
    db_session = SessionLocal()
    organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]
    db_session.close()

    conversation = None
    for slug in organization_slugs:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        # we close this later
        scoped_db_session = sessionmaker(bind=schema_engine)()
        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=scoped_db_session, channel_id=channel_id
        )

        if conversation:
            break

    return conversation


async def shortcut_context_middleware(body, context, next):
    """Attempts to determine the current context of the event."""
    context.update({"subject": SubjectMetadata(channel_id=context["channel_id"])})
    await next()


async def button_context_middleware(payload, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(payload["value"])})
    await next()


async def action_context_middleware(body, context, next):
    """Attempt to determine the current context of the event."""
    context.update({"subject": SubjectMetadata.parse_raw(body["view"]["private_metadata"])})
    await next()


async def message_context_middleware(context, next):
    """Attemps to determine the current context of the event."""
    conversation = resolve_conversation_from_context(context["channel_id"])
    if conversation:
        context.update(
            {
                "subject": SubjectMetadata(
                    type="incident",
                    id=conversation.incident.id,
                    organization_slug=conversation.incident.project.organization.slug,
                    project_id=conversation.incident.project.id,
                ),
                "db_session": Session.object_session(conversation),
            }
        )
    else:
        raise Exception("Unable to determine context.")

    await next()


async def restricted_command_middleware(context, db_session, user, next):
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

    raise Exception("Unauthorized.")


async def user_middleware(body, payload, db_session, client, context, next):
    """Attempts to determine the user making the request."""

    # for modals
    if body.get("user"):
        user_id = body["user"]["id"]

    # for messages
    if payload.get("user"):
        user_id = payload["user"]

    # for commands
    if payload.get("user_id"):
        user_id = payload["user_id"]

    email = (await client.users_info(user=user_id))["user"]["profile"]["email"]
    context["user"] = user_service.get_or_create(
        db_session=db_session,
        organization=context["subject"].organization_slug,
        user_in=DispatchUser(email=email),
    )
    await next()


async def modal_submit_middleware(body, context, next):
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


# TODO determine how we an get the current slack config
async def configuration_context_middleware(context, db_session, next):
    context["config"] = {}  # SlackConversationConfiguration()
    await next()


async def command_context_middleware(context, next):
    conversation = resolve_conversation_from_context(channel_id=context["channel_id"])
    if conversation:
        context.update(
            {
                "subject": SubjectMetadata(
                    type="incident",
                    id=conversation.incident.id,
                    organization_slug=conversation.incident.project.organization.slug,
                    project_id=conversation.incident.project.id,
                )
            }
        )
    else:
        raise Exception("Unable to determine context.")

    await next()


async def db_middleware(context, next):
    if context.get("db_session"):
        return await next()

    if not context.get("subject"):
        db_session = SessionLocal()
        slug = organization_service.get_default(db_session=db_session).slug
        context.update({"subject": SubjectMetadata(organization_slug=slug)})
        db_session.close()
    else:
        slug = context["subject"].organization_slug

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{slug}",
        }
    )
    context["db_session"] = sessionmaker(bind=schema_engine)()
    await next()
