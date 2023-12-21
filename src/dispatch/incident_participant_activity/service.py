from datetime import datetime, timedelta

from dispatch.database.core import SessionLocal
from dispatch.participant import service as participant_service
from dispatch.plugin import service as plugin_service

from .models import (
    IncidentParticipantActivity,
    IncidentParticipantActivityRead,
    IncidentParticipantActivityCreate,
    IncidentParticipantActivityUpdate,
)


def get_all_incident_participant_activities_from_last_update(
    db_session: SessionLocal,
    incident_id: int,
) -> list[IncidentParticipantActivityRead]:
    """Fetches the most recent recorded participant incident activities for each participant for a given incident."""
    return (
        db_session.query(IncidentParticipantActivity)
        .distinct(IncidentParticipantActivity.participant_id)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .order_by(
            IncidentParticipantActivity.participant_id, IncidentParticipantActivity.ended_at.desc()
        )
        .all()
    )


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


def get_last_incident_participant_activity(
    db_session: SessionLocal, incident_id: int
) -> IncidentParticipantActivity:
    """Returns the last recorded participant incident activity for a given incident."""
    return (
        db_session.query(IncidentParticipantActivity)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .order_by(IncidentParticipantActivity.ended_at.desc())
        .first()
    )


def get_all_incident_participant_activities_for_incident(
    db_session: SessionLocal,
    incident_id: int,
) -> list[IncidentParticipantActivityRead]:
    return (
        db_session.query(IncidentParticipantActivity)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .all()
    )


def get_incident_participant_activity_from_last_update(
    db_session: SessionLocal, incident_id: int, participant_id: int
) -> IncidentParticipantActivity:
    return (
        db_session.query(IncidentParticipantActivity)
        .filter(IncidentParticipantActivity.incident_id == incident_id)
        .filter(IncidentParticipantActivity.participant_id == participant_id)
        .order_by(IncidentParticipantActivity.ended_at.desc())
        .first()
    )


def create_or_update(
    db_session: SessionLocal, activity_in: IncidentParticipantActivityCreate
) -> timedelta:
    """Creates or updates a participant activity. Returns the change of the participant's total incident response time."""
    delta = timedelta(seconds=0)

    prev_activity = get_incident_participant_activity_from_last_update(
        db_session=db_session,
        incident_id=activity_in.incident.id,
        participant_id=activity_in.participant.id,
    )

    # There's continuous participant activity.
    if prev_activity and activity_in.started_at < prev_activity.ended_at:
        # Continuation of current plugin event.
        if activity_in.plugin_event.id == prev_activity.plugin_event.id:
            delta = activity_in.ended_at - prev_activity.ended_at
            prev_activity.ended_at = activity_in.ended_at
            db_session.commit()
            return delta

        # New activity is associated with a different plugin event.
        delta += activity_in.started_at - prev_activity.ended_at
        prev_activity.ended_at = activity_in.started_at

    create(db_session=db_session, activity_in=activity_in)
    delta += activity_in.ended_at - activity_in.started_at
    return delta


def get_participant_incident_activities_by_individual_contact(
    db_session: SessionLocal, individual_contact_id: int
) -> list[IncidentParticipantActivity]:
    """Fetches all recorded participant incident activities across all incidents for a given individual."""
    participants = participant_service.get_by_individual_contact_id(
        db_session=db_session, individual_id=individual_contact_id
    )

    return (
        db_session.query(IncidentParticipantActivity)
        .filter(
            IncidentParticipantActivity.participant_id.in_(
                [participant.id for participant in participants]
            )
        )
        .all()
    )


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
