def test_create_incident_participant_activity(
    session, incident_cost_model_activity, participant, incident
):
    from dispatch.incident_participant_activity.service import (
        create,
        get_all_incident_participant_activities_for_incident,
    )
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=incident_cost_model_activity.plugin_event,
        participant=participant,
        incident=incident,
    )

    activity_out = create(db_session=session, activity_in=activity_in)
    assert activity_out

    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident.id
    )
    assert activities
    assert activity_out in activities


def test_get_participant_incident_activities_by_individual_contact(
    session, incident_participant_activity, participant
):
    """Tests that we can get all incident participant activities for an individual across all incidents."""
    from dispatch.incident_participant_activity.service import (
        get_participant_incident_activities_by_individual_contact,
    )

    incident_participant_activity.participant = participant
    activities = get_participant_incident_activities_by_individual_contact(
        db_session=session,
        individual_contact_id=incident_participant_activity.participant.individual_contact_id,
    )

    assert activities
    assert incident_participant_activity.id in [activity.id for activity in activities]


def test_create_or_update_incident_participant_activity__same_plugin_no_overlap(
    session, incident_participant_activity
):
    """Tests that a new incident participant activity is created when there is no time overlap with previously recorded activities."""
    from datetime import timedelta
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate
    from dispatch.incident_participant_activity.service import (
        create_or_update,
        get_all_incident_participant_activities_for_incident,
    )

    orig_activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )

    started_at = incident_participant_activity.ended_at + timedelta(seconds=1)
    ended_at = incident_participant_activity.ended_at + timedelta(seconds=10)

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=incident_participant_activity.plugin_event,
        started_at=started_at,
        ended_at=ended_at,
        participant=incident_participant_activity.participant,
        incident=incident_participant_activity.incident,
    )

    assert ended_at - started_at == create_or_update(db_session=session, activity_in=activity_in)
    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )
    assert activities
    assert len(activities) == len(orig_activities) + 1
    assert incident_participant_activity.id in [activity.id for activity in activities]


def test_create_or_update_incident_participant_activity__new_plugin_no_overlap(
    session, incident_participant_activity, plugin_event
):
    """Tests that a new incident participant activity is created when there is no time overlap with previously recorded activities."""
    from datetime import timedelta
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate
    from dispatch.incident_participant_activity.service import (
        create_or_update,
        get_all_incident_participant_activities_for_incident,
    )

    assert incident_participant_activity.plugin_event.id != plugin_event.id
    orig_activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )

    started_at = incident_participant_activity.ended_at + timedelta(seconds=1)
    ended_at = started_at + timedelta(seconds=10)

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=plugin_event,
        started_at=started_at,
        ended_at=ended_at,
        participant=incident_participant_activity.participant,
        incident=incident_participant_activity.incident,
    )
    assert ended_at - started_at == create_or_update(db_session=session, activity_in=activity_in)

    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )
    assert activities
    assert len(activities) == len(orig_activities) + 1
    assert incident_participant_activity.id in [activity.id for activity in activities]


def test_create_or_update_incident_participant_activity__same_plugin_with_overlap(
    session, incident_participant_activity
):
    """Tests only updating an existing incident participant activity.

    Tests that the previously recorded incident participant activity is updated when there is continuous activity with the same plugin event.
    """
    from datetime import timedelta
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate
    from dispatch.incident_participant_activity.service import (
        create_or_update,
        get_all_incident_participant_activities_for_incident,
    )

    orig_activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )

    # Start new incident activity in the middle of the existing recorded incident activity.
    started_at = (
        incident_participant_activity.started_at
        + (incident_participant_activity.ended_at - incident_participant_activity.started_at) / 2
    )
    ended_at = incident_participant_activity.ended_at + timedelta(seconds=10)

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=incident_participant_activity.plugin_event,
        started_at=started_at,
        ended_at=ended_at,
        participant=incident_participant_activity.participant,
        incident=incident_participant_activity.incident,
    )

    assert timedelta(seconds=10) == create_or_update(db_session=session, activity_in=activity_in)
    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )
    assert activities
    assert len(activities) == len(orig_activities)
    assert incident_participant_activity.id in [activity.id for activity in activities]


def test_create_or_update_incident_participant_activity__new_plugin_with_overlap(
    session, incident_participant_activity, plugin_event
):
    """Tests updating an existing incident participant activity and creating a new incident participant activity.

    Tests that the previously recorded incident participant activity is updated and a new incident participant
    activity is created when there is continuous participant activity coming from a different plugin event.
    """
    from datetime import timedelta
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate
    from dispatch.incident_participant_activity.service import (
        create_or_update,
        get_all_incident_participant_activities_for_incident,
    )

    assert incident_participant_activity.plugin_event.id != plugin_event.id
    orig_activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )

    # Start new incident activity in the middle of the existing recorded incident activity.
    started_at = (
        incident_participant_activity.started_at
        + (incident_participant_activity.ended_at - incident_participant_activity.started_at) / 2
    )
    ended_at = incident_participant_activity.ended_at + timedelta(seconds=10)

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=plugin_event,
        started_at=started_at,
        ended_at=ended_at,
        participant=incident_participant_activity.participant,
        incident=incident_participant_activity.incident,
    )

    assert timedelta(seconds=10) == create_or_update(db_session=session, activity_in=activity_in)
    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident_participant_activity.incident.id
    )
    assert activities
    assert len(activities) == len(orig_activities) + 1
    assert incident_participant_activity.id in [activity.id for activity in activities]


def test_get_incidents_by_plugin(session, incident_participant_activity):
    from dispatch.incident_participant_activity.service import (
        get_all_recorded_incident_partcipant_activities_for_plugin,
    )

    activities = get_all_recorded_incident_partcipant_activities_for_plugin(
        db_session=session,
        incident_id=incident_participant_activity.incident.id,
        plugin_id=incident_participant_activity.plugin_event.plugin.id,
    )

    assert activities
    assert incident_participant_activity.id in [activity.id for activity in activities]
