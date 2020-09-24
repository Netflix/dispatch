import arrow
import datetime

from typing import List
from pydantic import BaseModel

from dispatch.decorators import background_task
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_service
from dispatch.participant import service as participant_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from .config import (
    SLACK_TIMELINE_EVENT_REACTION,
    SLACK_BAN_THREADS,
)

from .service import get_user_email

slack_client = dispatch_slack_service.create_slack_client()


class EventBodyItem(BaseModel):
    """Body item of the Slack event."""

    type: str = None
    channel: str = None
    ts: str = None


class EventBody(BaseModel):
    """Body of the Slack event."""

    channel: str = None
    channel_id: str = None
    channel_type: str = None
    deleted_ts: str = None
    event_ts: str = None
    thread_ts: str = None
    file_id: str = None
    hidden: bool = None
    inviter: str = None
    item: EventBodyItem = None
    item_user: str = None
    reaction: str = None
    subtype: str = None
    team: str = None
    text: str = None
    type: str
    user: str = None
    user_id: str = None


class EventEnvelope(BaseModel):
    """Envelope of the Slack event."""

    api_app_id: str = None
    authed_users: List[str] = []
    challenge: str = None
    enterprise_id: str = None
    event: EventBody = None
    event_id: str = None
    event_time: int = None
    team_id: str = None
    token: str = None
    type: str


def get_channel_id_from_event(event_body: dict):
    """Returns the channel id from the Slack event."""
    channel_id = ""
    if event_body.channel_id:
        return event_body.channel_id
    if event_body.channel:
        return event_body.channel
    if event_body.item.channel:
        return event_body.item.channel

    return channel_id


def event_functions(event: EventEnvelope):
    """Interprets the events and routes it the appropriate function."""
    event_mappings = {
        "member_joined_channel": [member_joined_channel],
        "member_left_channel": [incident_flows.incident_remove_participant_flow],
        "message": [after_hours, ban_threads_warning],
        "message.groups": [],
        "message.im": [],
        "reaction_added": [handle_reaction_added_event],
    }

    return event_mappings.get(event.event.type, [])


@background_task
def handle_reaction_added_event(
    user_email: str, incident_id: int, event: dict = None, db_session=None
):
    """Handles an event where a reaction is added to a message."""
    reaction = event.event.reaction

    if reaction == SLACK_TIMELINE_EVENT_REACTION:
        conversation_id = event.event.item.channel
        message_ts = event.event.item.ts
        message_ts_utc = datetime.datetime.utcfromtimestamp(float(message_ts))

        # we fetch the message information
        response = dispatch_slack_service.list_conversation_messages(
            slack_client, conversation_id, latest=message_ts, limit=1, inclusive=1
        )
        message_text = response["messages"][0]["text"]
        message_sender_id = response["messages"][0]["user"]

        # we fetch the individual who sent the message
        message_sender_email = get_user_email(client=slack_client, user_id=message_sender_id)
        individual = individual_service.get_by_email(
            db_session=db_session, email=message_sender_email
        )

        # we log the event
        event_service.log(
            db_session=db_session,
            source="Slack Plugin - Conversation Management",
            description=f'"{message_text}," said {individual.name}',
            incident_id=incident_id,
            individual_id=individual.id,
            started_at=message_ts_utc,
        )


def is_business_hours(commander_tz: str):
    """Determines if it's currently office hours where the incident commander is located."""
    now = arrow.utcnow().to(commander_tz)
    return now.weekday() not in [5, 6] and 9 <= now.hour < 17


@background_task
def after_hours(user_email: str, incident_id: int, event: dict = None, db_session=None):
    """Notifies the user that this incident is current in after hours mode."""
    # we want to ignore user joined messages
    if event.event.subtype == "group_join":
        return

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # get their timezone from slack
    commander_info = dispatch_slack_service.get_user_info_by_email(
        slack_client, email=incident.commander.email
    )

    commander_tz = commander_info["tz"]

    if not is_business_hours(commander_tz):
        # send ephermal message
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        (
                            f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}*"
                            f" and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {commander_tz} timezone)."
                        )
                    ),
                },
            }
        ]

        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=incident_id, email=user_email
        )
        if not participant.after_hours_notification:
            user_id = dispatch_slack_service.resolve_user(slack_client, user_email)["id"]
            dispatch_slack_service.send_ephemeral_message(
                slack_client, incident.conversation.channel_id, user_id, "", blocks=blocks
            )
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()


@background_task
def member_joined_channel(
    user_email: str,
    incident_id: int,
    event: EventEnvelope,
    db_session=None,
):
    """Handles the member_joined_channel slack event."""
    participant = incident_flows.incident_add_or_reactivate_participant_flow(
        user_email=user_email, incident_id=incident_id, db_session=db_session
    )

    if event.event.inviter:
        # we update the participant's metadata
        if not dispatch_slack_service.is_user(event.event.inviter):
            # we default to the incident commander when we don't know how the user was added
            participant.added_by = participant_service.get_by_incident_id_and_role(
                db_session=db_session,
                incident_id=incident_id,
                role=ParticipantRoleType.incident_commander,
            )
            participant.added_reason = "User was automatically added by Dispatch."

        else:
            inviter_email = get_user_email(client=slack_client, user_id=event.event.inviter)
            added_by_participant = participant_service.get_by_incident_id_and_email(
                db_session=db_session, incident_id=incident_id, email=inviter_email
            )
            participant.added_by = added_by_participant
            participant.added_reason = event.event.text

        db_session.commit()


@background_task
def ban_threads_warning(user_email: str, incident_id: int, event: dict = None, db_session=None):
    """Sends the user an ephemeral message if they use threads."""
    if not SLACK_BAN_THREADS:
        return

    if event.event.thread_ts:
        # we should be able to look for `subtype == message_replied` once this bug is fixed
        # https://api.slack.com/events/message/message_replied
        # From Slack: Bug alert! This event is missing the subtype field when dispatched
        # over the Events API. Until it is fixed, examine message events' thread_ts value.
        # When present, it's a reply. To be doubly sure, compare a thread_ts to the top-level ts
        # value, when they differ the latter is a reply to the former.
        message = "Please refrain from using threads in incident related channels. Threads make it harder for incident participants to maintain context."
        dispatch_slack_service.send_ephemeral_message(
            slack_client,
            event.event.channel,
            event.event.user,
            message,
            thread_ts=event.event.thread_ts,
        )
