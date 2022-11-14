import pytz
from datetime import datetime

from dispatch.database.core import SessionLocal
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentUpdate, IncidentRead, IncidentCreate
from dispatch.individual.models import IndividualContactRead
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.plugin import service as plugin_service
from dispatch.tag import service as tag_service

from dispatch.plugins.dispatch_slack.decorators import slack_background_task
from dispatch.plugins.dispatch_slack.messaging import create_incident_reported_confirmation_message
from dispatch.plugins.dispatch_slack.service import (
    send_ephemeral_message,
    open_modal_with_user,
    update_modal_with_user,
    get_user_profile_by_email,
)
from dispatch.plugins.dispatch_slack.modals.common import parse_submitted_form
from dispatch.plugins.dispatch_slack.config import SlackConversationConfiguration

from .enums import (
    IncidentBlockId,
    UpdateParticipantBlockId,
    UpdateNotificationsGroupBlockId,
    AddTimelineEventBlockId,
)
from .views import (
    update_incident,
    report_incident,
    update_participant,
    update_notifications_group,
    add_timeline_event,
)


# report incident
@slack_background_task
def create_report_incident_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    config: SlackConversationConfiguration = None,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for reporting an incident."""
    trigger_id = command.get("trigger_id")
    modal_create_template = report_incident(channel_id=channel_id, db_session=db_session)
    open_modal_with_user(client=slack_client, trigger_id=trigger_id, modal=modal_create_template)


@slack_background_task
def update_report_incident_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict = None,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for reporting an incident."""
    trigger_id = action["trigger_id"]

    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    # we must pass existing values if they exist
    modal_update_template = report_incident(
        db_session=db_session,
        channel_id=channel_id,
        title=parsed_form_data[IncidentBlockId.title],
        description=parsed_form_data[IncidentBlockId.description],
        project_name=parsed_form_data[IncidentBlockId.project]["value"],
    )

    update_modal_with_user(
        client=slack_client,
        trigger_id=trigger_id,
        view_id=action["view"]["id"],
        modal=modal_update_template,
    )


@slack_background_task
def report_incident_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session: SessionLocal = None,
    slack_client=None,
):
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    # Send a confirmation to the user
    blocks = create_incident_reported_confirmation_message(
        title=parsed_form_data[IncidentBlockId.title],
        description=parsed_form_data[IncidentBlockId.description],
        incident_type=parsed_form_data[IncidentBlockId.type]["value"],
        incident_priority=parsed_form_data[IncidentBlockId.priority]["value"],
    )

    send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="",
        blocks=blocks,
    )

    tags = []
    for t in parsed_form_data.get(IncidentBlockId.tags, []):
        # we have to fetch as only the IDs are embedded in slack
        tag = tag_service.get(db_session=db_session, tag_id=int(t["value"]))
        tags.append(tag)

    project = {"name": parsed_form_data[IncidentBlockId.project]["value"]}
    incident_in = IncidentCreate(
        title=parsed_form_data[IncidentBlockId.title],
        description=parsed_form_data[IncidentBlockId.description],
        incident_type={"name": parsed_form_data[IncidentBlockId.type]["value"]},
        incident_priority={"name": parsed_form_data[IncidentBlockId.priority]["value"]},
        project=project,
        tags=tags,
    )

    if not incident_in.reporter:
        incident_in.reporter = ParticipantUpdate(individual=IndividualContactRead(email=user_email))

    # Create the incident
    incident = incident_service.create(db_session=db_session, incident_in=incident_in)

    incident_flows.incident_create_flow(
        incident_id=incident.id,
        db_session=db_session,
        organization_slug=incident.project.organization.slug,
    )


# update incident
@slack_background_task
def create_update_incident_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    config: SlackConversationConfiguration = None,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a dialog for updating incident information."""
    modal = update_incident(db_session=db_session, channel_id=channel_id, incident_id=incident_id)
    open_modal_with_user(client=slack_client, trigger_id=command["trigger_id"], modal=modal)


@slack_background_task
def update_incident_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Massages slack dialog data into something that Dispatch can use."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    tags = []
    for t in parsed_form_data.get(IncidentBlockId.tags, []):
        # we have to fetch as only the IDs are embedded in slack
        tag = tag_service.get(db_session=db_session, tag_id=int(t["value"]))
        tags.append(tag)

    incident_in = IncidentUpdate(
        title=parsed_form_data[IncidentBlockId.title],
        description=parsed_form_data[IncidentBlockId.description],
        resolution=parsed_form_data[IncidentBlockId.resolution],
        incident_type={"name": parsed_form_data[IncidentBlockId.type]["value"]},
        incident_severity={"name": parsed_form_data[IncidentBlockId.severity]["value"]},
        incident_priority={"name": parsed_form_data[IncidentBlockId.priority]["value"]},
        status=parsed_form_data[IncidentBlockId.status]["value"],
        tags=tags,
    )

    previous_incident = IncidentRead.from_orm(incident)

    # we currently don't allow users to update the incident's visibility,
    # costs, terms, or duplicates via Slack, so we copy them over
    incident_in.visibility = incident.visibility
    incident_in.incident_costs = incident.incident_costs
    incident_in.terms = incident.terms
    incident_in.duplicates = incident.duplicates

    updated_incident = incident_service.update(
        db_session=db_session, incident=incident, incident_in=incident_in
    )

    commander_email = updated_incident.commander.individual.email
    reporter_email = updated_incident.reporter.individual.email
    incident_flows.incident_update_flow(
        user_email,
        commander_email,
        reporter_email,
        incident_id,
        previous_incident,
        db_session=db_session,
    )

    if updated_incident.status != IncidentStatus.closed:
        send_ephemeral_message(
            slack_client, channel_id, user_id, "You have sucessfully updated the incident."
        )


# update participant
@slack_background_task
def create_update_participant_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for updating a participant."""
    trigger_id = command["trigger_id"]
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    modal_create_template = update_participant(incident=incident)
    open_modal_with_user(client=slack_client, trigger_id=trigger_id, modal=modal_create_template)


@slack_background_task
def update_update_participant_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Pushes an updated view to the update participant modal."""
    trigger_id = action["trigger_id"]

    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    participant_id = parsed_form_data[UpdateParticipantBlockId.participant]["value"]

    selected_participant = participant_service.get(
        db_session=db_session, participant_id=participant_id
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    modal_update_template = update_participant(incident=incident, participant=selected_participant)

    update_modal_with_user(
        client=slack_client,
        trigger_id=trigger_id,
        view_id=action["view"]["id"],
        modal=modal_update_template,
    )


@slack_background_task
def update_participant_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Saves form data."""
    submitted_form = action.get("view")

    parsed_form_data = parse_submitted_form(submitted_form)

    added_reason = parsed_form_data.get(UpdateParticipantBlockId.reason_added)
    participant_id = int(parsed_form_data.get(UpdateParticipantBlockId.participant)["value"])
    selected_participant = participant_service.get(
        db_session=db_session, participant_id=participant_id
    )
    participant_service.update(
        db_session=db_session,
        participant=selected_participant,
        participant_in=ParticipantUpdate(added_reason=added_reason),
    )

    send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="You have successfully updated the participant.",
    )


# update notification group
@slack_background_task
def create_update_notifications_group_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for editing members of the notifications group."""
    trigger_id = command["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_create_template = update_notifications_group(incident=incident, db_session=db_session)

    open_modal_with_user(client=slack_client, trigger_id=trigger_id, modal=modal_create_template)


@slack_background_task
def update_notifications_group_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Updates notifications group based on submitted form data."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    current_members = (
        submitted_form["blocks"][1]["element"]["initial_value"].replace(" ", "").split(",")
    )
    updated_members = (
        parsed_form_data.get(UpdateNotificationsGroupBlockId.update_members)
        .replace(" ", "")
        .split(",")
    )

    members_added = list(set(updated_members) - set(current_members))
    members_removed = list(set(current_members) - set(updated_members))

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )

    group_plugin.instance.add(incident.notifications_group.email, members_added)
    group_plugin.instance.remove(incident.notifications_group.email, members_removed)

    send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="You have successfully updated the notifications group.",
    )


# add event
@slack_background_task
def create_add_timeline_event_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for adding events to the incident timeline."""
    trigger_id = command["trigger_id"]
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    modal_create_template = add_timeline_event(incident=incident)
    open_modal_with_user(client=slack_client, trigger_id=trigger_id, modal=modal_create_template)


@slack_background_task
def add_timeline_event_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    config: SlackConversationConfiguration = None,
    db_session=None,
    slack_client=None,
):
    """Adds event to incident timeline based on submitted form data."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    event_date = parsed_form_data.get(AddTimelineEventBlockId.date)
    event_hour = parsed_form_data.get(AddTimelineEventBlockId.hour)["value"]
    event_minute = parsed_form_data.get(AddTimelineEventBlockId.minute)["value"]
    event_timezone_selection = parsed_form_data.get(AddTimelineEventBlockId.timezone)["value"]
    event_description = parsed_form_data.get(AddTimelineEventBlockId.description)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    event_timezone = event_timezone_selection
    if event_timezone_selection == "profile":
        participant_profile = get_user_profile_by_email(slack_client, user_email)
        if participant_profile.get("tz"):
            event_timezone = participant_profile.get("tz")

    event_dt = datetime.fromisoformat(f"{event_date}T{event_hour}:{event_minute}")
    event_dt_utc = pytz.timezone(event_timezone).localize(event_dt).astimezone(pytz.utc)

    event_service.log_incident_event(
        db_session=db_session,
        source="Slack Plugin - Conversation Management",
        started_at=event_dt_utc,
        description=f'"{event_description}," said {participant.individual.name}',
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="Event sucessfully added to timeline.",
    )
