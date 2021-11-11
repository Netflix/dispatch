import pytz
import logging
import datetime

from typing import List
from pydantic import BaseModel
from sqlalchemy import func

from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.conversation import service as conversation_service
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.plugins.dispatch_slack.config import (
    SlackConversationConfiguration,
)
from dispatch.tag import service as tag_service
from dispatch.individual import service as individual_service
from dispatch.participant import service as participant_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugin import service as plugin_service
from dispatch.monitor import service as monitor_service
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.tag.models import Tag


from .decorators import slack_background_task, get_organization_scope_from_channel_id
from .service import get_user_email
from .models import MonitorButton


log = logging.getLogger(__name__)


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


def get_channel_id_from_event(event: EventEnvelope):
    """Returns the channel id from the Slack event."""
    channel_id = ""
    if event.event.channel_id:
        return event.event.channel_id
    if event.event.channel:
        return event.event.channel
    if event.event.item.channel:
        return event.event.item.channel
    return channel_id


def event_functions(event: EventEnvelope):
    """Interprets the events and routes it the appropriate function."""
    event_mappings = {
        "member_joined_channel": [member_joined_channel],
        "member_left_channel": [member_left_channel],
        "message": [
            increment_activity,
            after_hours,
            ban_threads_warning,
            message_tagging,
            message_monitor,
        ],
        "message.groups": [],
        "message.im": [],
        "reaction_added": [handle_reaction_added_event],
    }
    return event_mappings.get(event.event.type, [])


async def handle_slack_event(*, config, client, event, background_tasks):
    """Handles slack event message."""
    user_id = event.event.user
    channel_id = get_channel_id_from_event(event)

    if user_id and channel_id:
        db_session = get_organization_scope_from_channel_id(channel_id=channel_id)

        if not db_session:
            log.info(
                f"Unable to determine organization associated with channel id. ChannelId: {channel_id}"
            )
            return {"ok": ""}

        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=db_session, channel_id=channel_id
        )

        if conversation and dispatch_slack_service.is_user(config, user_id):
            # We resolve the user's email
            user_email = await dispatch_slack_service.get_user_email_async(client, user_id)
            # Dispatch event functions to be executed in the background
            for f in event_functions(event):
                background_tasks.add_task(
                    f,
                    config=config,
                    user_id=user_id,
                    user_email=user_email,
                    channel_id=channel_id,
                    incident_id=conversation.incident_id,
                    event=event,
                )

    return {"ok": ""}


@slack_background_task
def handle_reaction_added_event(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    """Handles an event where a reaction is added to a message."""
    reaction = event.event.reaction

    if reaction == config.timeline_event_reaction:
        conversation_id = event.event.item.channel
        message_ts = event.event.item.ts
        message_ts_utc = datetime.datetime.utcfromtimestamp(float(message_ts))

        # we fetch the message information
        response = dispatch_slack_service.list_conversation_messages(
            slack_client, conversation_id, latest=message_ts, limit=1, inclusive=1
        )
        message_text = response["messages"][0]["text"]
        message_sender_id = response["messages"][0]["user"]

        # we fetch the incident
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)

        # we fetch the individual who sent the message
        message_sender_email = get_user_email(client=slack_client, user_id=message_sender_id)
        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=message_sender_email, project_id=incident.project.id
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


@slack_background_task
def increment_activity(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    # increment activity for user
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # member join also creates a message but they aren't yet a participant
    if participant:
        if participant.activity:
            participant.activity += 1
        else:
            participant.activity = 1

        db_session.commit()


def is_business_hours(commander_tz: str):
    """Determines if it's currently office hours where the incident commander is located."""
    now = datetime.datetime.now(pytz.timezone(commander_tz))
    return now.weekday() not in [5, 6] and 9 <= now.hour < 17


@slack_background_task
def after_hours(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    """Notifies the user that this incident is current in after hours mode."""
    # we ignore user channel and group join messages
    if event.event.subtype in ["channel_join", "group_join"]:
        return

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # get their timezone from slack
    commander_info = dispatch_slack_service.get_user_info_by_email(
        slack_client, email=incident.commander.individual.email
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
            dispatch_slack_service.send_ephemeral_message(
                slack_client, channel_id, user_id, "", blocks=blocks
            )
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()


@slack_background_task
def member_joined_channel(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope,
    db_session=None,
    slack_client=None,
):
    """Handles the member_joined_channel slack event."""
    participant = incident_flows.incident_add_or_reactivate_participant_flow(
        user_email=user_email, incident_id=incident_id, db_session=db_session
    )

    if event.event.inviter:
        # we update the participant's metadata
        if not dispatch_slack_service.is_user(config, event.event.inviter):
            # we default to the incident commander when we don't know how the user was added
            added_by_participant = participant_service.get_by_incident_id_and_role(
                db_session=db_session,
                incident_id=incident_id,
                role=ParticipantRoleType.incident_commander,
            )
            participant.added_by = added_by_participant
            participant.added_reason = (
                f"Participant added by {added_by_participant.individual.name}"
            )

        else:
            inviter_email = get_user_email(client=slack_client, user_id=event.event.inviter)
            added_by_participant = participant_service.get_by_incident_id_and_email(
                db_session=db_session, incident_id=incident_id, email=inviter_email
            )
            participant.added_by = added_by_participant
            participant.added_reason = event.event.text

        db_session.add(participant)
        db_session.commit()


@slack_background_task
def member_left_channel(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope,
    db_session=None,
    slack_client=None,
):
    """Handles the member_left_channel Slack event."""
    incident_flows.incident_remove_participant_flow(user_email, incident_id, db_session=db_session)


@slack_background_task
def ban_threads_warning(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    """Sends the user an ephemeral message if they use threads."""
    if not config.ban_threads:
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
            channel_id,
            user_id,
            message,
            thread_ts=event.event.thread_ts,
        )


@slack_background_task
def message_tagging(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    """Looks for incident tags in incident messages."""
    text = event.event.text
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    tags = tag_service.get_all(db_session=db_session, project_id=incident.project.id).all()
    tag_strings = [t.name.lower() for t in tags if t.discoverable]
    phrases = build_term_vocab(tag_strings)
    matcher = build_phrase_matcher("dispatch-tag", phrases)
    extracted_tags = list(set(extract_terms_from_text(text, matcher)))

    matched_tags = (
        db_session.query(Tag)
        .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
        .all()
    )

    incident.tags.extend(matched_tags)
    db_session.commit()


@slack_background_task
def message_monitor(
    config: SlackConversationConfiguration,
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    event: EventEnvelope = None,
    db_session=None,
    slack_client=None,
):
    """Looks strings that are available for monitoring (usually links)."""
    text = event.event.text
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    plugins = plugin_service.get_active_instances(
        db_session=db_session, project_id=incident.project.id, plugin_type="monitor"
    )

    for p in plugins:
        for matcher in p.instance.get_matchers():
            for match in matcher.finditer(text):
                match_data = match.groupdict()
                monitor = monitor_service.get_by_weblink(
                    db_session=db_session, weblink=match_data["weblink"]
                )

                # silence ignored matches
                if monitor:
                    continue

                current_status = p.instance.get_match_status(match_data)
                if current_status:
                    status_text = ""
                    for k, v in current_status.items():
                        status_text += f"*{k.title()}*:\n{v.title()}\n"

                    monitor_button = MonitorButton(
                        incident_id=incident.id,
                        plugin_instance_id=p.id,
                        organization=incident.project.organization.slug,
                        weblink=match_data["weblink"],
                        action_type="monitor",
                    )

                    ignore_button = MonitorButton(
                        incident_id=incident.id,
                        plugin_instance_id=p.id,
                        organization=incident.project.organization.slug,
                        weblink=match_data["weblink"],
                        action_type="ignore",
                    )

                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Hi! Dispatch is able to help track the status of: \n {match_data['weblink']} \n\n Would you like for changes in it's status to be propagated to this incident channel?",
                            },
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": status_text,
                            },
                        },
                        {
                            "type": "actions",
                            "block_id": f"{ConversationButtonActions.monitor_link}",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "emoji": True,
                                        "text": "Monitor",
                                    },
                                    "style": "primary",
                                    "value": monitor_button.json(),
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "emoji": True, "text": "Ignore"},
                                    "style": "danger",
                                    "value": ignore_button.json(),
                                },
                            ],
                        },
                    ]

                    dispatch_slack_service.send_ephemeral_message(
                        slack_client, channel_id, user_id, "", blocks=blocks
                    )
