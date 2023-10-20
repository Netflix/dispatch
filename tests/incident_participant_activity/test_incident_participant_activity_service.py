def test_create_incident_participant_activity(
    session, incident_cost_model_activity, participant, incident
):
    from dispatch.incident_participant_activity.service import (
        create,
        get_all_incident_participant_activities,
    )
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate

    activity_in = IncidentParticipantActivityCreate(
        plugin_event=incident_cost_model_activity.event,
        participant=participant,
        incident=incident,
    )

    activity_out = create(db_session=session, activity_in=activity_in)
    assert activity_out

    activities = get_all_incident_participant_activities(
        db_session=session, incident_id=incident.id
    )
    assert activities
    assert activity_out in activities


# Running both test_create_incident_participant_activity and test_get_incident_activities_by_individual results in flaky test results.
def test_get_incident_activities_by_individual(session, incident_participant_activity):
    from dispatch.incident_participant_activity.service import (
        get_participant_incident_activities_by_individual_contact,
    )

    activities = get_participant_incident_activities_by_individual_contact(
        db_session=session,
        incident_id=incident_participant_activity.incident.id,
        individual_contact_id=incident_participant_activity.participant.individual_contact_id,
    )

    assert activities
    assert incident_participant_activity.id in [activity.id for activity in activities]


# TODO(averyl): create a list of incident participant activities to serve as the existing base.
# create 4 new incident participant activities.
# 1. unique plugin with overlap time -> last existing item should be curtailed at starting time? new item has starting time
# 2. unique plugin with no overlap time -> new item should be created
# 3. existing plugin with overlap time -> last existing item should be updated with new ending time
# 4. existing plugin with no overlap time -> new item should be created
def test_create_or_update_incident_activities(session, incident_participant_activity):
    # from dispatch.incident_participant_activity.service import create_or_update
    from pprint import pprint

    mutations = []

    pass


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
