from datetime import datetime
from sqlalchemy import func, select

from .models import (
    IncidentParticipantActivity,
    IncidentParticipantActivityRead,
    IncidentParticipantActivityCreate,
    IncidentParticipantActivityUpdate,
)
from dispatch.database.core import SessionLocal
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.plugin import service as plugin_service


# TODO(averyl) records user activity in the db
# def create_incident_activity_for_user(
#     db_session: SessionLocal, incident_id: int, individual_contact_id: int
# ):
# check the last record in the table for the incident, individual, activity timestamp, activity
# filtering: the ended_at of the recorded activity should occur after the last update_time.

# if the last record has exceeded the duration for that activity, then create a new record
# else, update the last record's ended_at
#   if the last activity is the same as this current activity, update the last record's ended_at
#   elif the last activity is different from this current activity, set the ended at for the last activity to the current activity's started_at.
#       create a new record for the current activity.

# corner case:
# if the last record's ended_at is overlapped with the current activity's started_at, then we need to update the last record's ended_at to the current activity's started_at.
# update the incident cost if needed
# pass


# TODO(averyl): finish this tomorrow. use the above logic
def create_or_update(
    db_session: SessionLocal, activity_in: IncidentParticipantActivityCreate
) -> IncidentParticipantActivity:
    prev_participant_activities = get_all_incident_participant_activities_from_last_update(
        db_session=db_session, incident_id=activity_in.incident.id
    )

    for activity in prev_participant_activities:
        if activity.plugin_event.id == activity_in.plugin_event.id:
            activity.ended_at = activity_in.ended_at
            db_session.commit()
            return activity

    incident_participant_activity = IncidentParticipantActivity()
    incident_participant_activity.plugin_event_id = activity_in.plugin_event.id
    incident_participant_activity.participant_id = activity_in.participant.id
    incident_participant_activity.incident_id = activity_in.incident.id

    db_session.add(incident_participant_activity)
    db_session.commit()

    return incident_participant_activity


def create(*, db_session: SessionLocal, activity_in: IncidentParticipantActivityCreate):
    activity = IncidentParticipantActivity(
        plugin_event_id=activity_in.plugin_event.id,
        started_at=activity_in.started_at,
        ended_at=activity_in.ended_at,
        participant_id=activity_in.participant.id,
        incident_id=activity_in.incident.id,
    )

    db_session.add(activity)
    db_session.commit()

    return activity


def update(
    *,
    db_session: SessionLocal,
    activity: IncidentParticipantActivity,
    activity_in: IncidentParticipantActivityUpdate,
) -> IncidentParticipantActivity:
    activity.ended_at = activity_in.ended_at
    db_session.commit()
    return activity


def get_all_incident_participant_activities(
    db_session: SessionLocal,
    incident_id: int,
) -> list[IncidentParticipantActivityRead]:
    return (
        db_session.query(IncidentParticipantActivity)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .all()
    )


def get_all_incident_participant_activities_from_last_update(
    db_session: SessionLocal,
    incident_id: int,
) -> list[IncidentParticipantActivityRead]:
    """Fetches the most recent recorded participant incident activities for each participant for a given incident."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    subquery = db_session.query(
        IncidentParticipantActivity.participant_id, func.max(IncidentParticipantActivity.ended_at)
    ).group_by(IncidentParticipantActivity.participant_id)

    return (
        db_session.query(IncidentParticipantActivity, func.max())
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .filter(IncidentParticipantActivity.ended_at > incident.updated_at)
        .filter(IncidentParticipantActivity.participant_id.in_(select(subquery)))
        .all()
    )


# Used for calculating the number of hours a particilar individual has spent on incidents.
def get_participant_incident_activities_by_individual_contact(
    db_session: SessionLocal, incident_id: int, individual_contact_id: int
) -> list[IncidentParticipantActivity]:
    participant = participant_service.get_by_individual_contact_id(
        db_session=db_session, individual_id=individual_contact_id
    )
    return (
        db_session.query(IncidentParticipantActivity)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .filter(IncidentParticipantActivity.participant_id == participant.id)
        .all()
    )


# showing recorded incident activities by plugin.
# This is used for calculating the time spent in each activity.
def get_all_recorded_incident_partcipant_activities_for_plugin(
    db_session: SessionLocal,
    incident_id: int,
    plugin_id: int,
    started_at: datetime = datetime.min,
    ended_at: datetime = datetime.utcnow(),
) -> list[IncidentParticipantActivityRead]:
    """Fetches all recorded participant incident activities for a given plugin."""

    plugin_events = plugin_service.get_all_events_for_plugin(
        db_session=db_session, plugin_id=plugin_id
    )
    participant_activities_for_plugin = []

    for plugin_event in plugin_events:
        event_activities = (
            db_session.query(IncidentParticipantActivity)
            .filter(IncidentParticipantActivity.incident_id == incident_id)
            .filter(IncidentParticipantActivity.plugin_event_id == plugin_event.id)
            .filter(IncidentParticipantActivity.started_at >= started_at)
            .filter(IncidentParticipantActivity.ended_at <= ended_at)
            .all()
        )
        participant_activities_for_plugin.extend(event_activities)

    return participant_activities_for_plugin
