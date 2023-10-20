import logging
import math
from datetime import datetime

from typing import List, Optional

from dispatch.database.core import SessionLocal
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.service import service as service_service
from dispatch.participant.models import ParticipantRead

from .models import IncidentCost, IncidentCostCreate, IncidentCostUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
log = logging.getLogger(__name__)


def get(*, db_session, incident_cost_id: int) -> Optional[IncidentCost]:
    """Gets an incident cost by its id."""
    return db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).one_or_none()


def get_by_incident_id(*, db_session, incident_id: int) -> List[Optional[IncidentCost]]:
    """Gets incident costs by their incident id."""
    return db_session.query(IncidentCost).filter(IncidentCost.incident_id == incident_id)


def get_by_incident_id_and_incident_cost_type_id(
    *, db_session, incident_id: int, incident_cost_type_id: int
) -> List[Optional[IncidentCost]]:
    """Gets incident costs by their incident id and incident cost type id."""
    return (
        db_session.query(IncidentCost)
        .filter(IncidentCost.incident_id == incident_id)
        .filter(IncidentCost.incident_cost_type_id == incident_cost_type_id)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[IncidentCost]]:
    """Gets all incident costs."""
    return db_session.query(IncidentCost)


def get_or_create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """Gets or creates an incident cost."""
    if incident_cost_in.id:
        incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_in.id)
    else:
        incident_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)

    return incident_cost


def create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """Creates a new incident cost."""
    incident_cost_type = incident_cost_type_service.get(
        db_session=db_session, incident_cost_type_id=incident_cost_in.incident_cost_type.id
    )
    incident_cost = IncidentCost(
        **incident_cost_in.dict(exclude={"incident_cost_type", "project"}),
        incident_cost_type=incident_cost_type,
        project=incident_cost_type.project,
    )
    db_session.add(incident_cost)
    db_session.commit()

    return incident_cost


def update(
    *, db_session, incident_cost: IncidentCost, incident_cost_in: IncidentCostUpdate
) -> IncidentCost:
    """Updates an incident cost."""
    incident_cost_data = incident_cost.dict()
    update_data = incident_cost_in.dict(skip_defaults=True)

    for field in incident_cost_data:
        if field in update_data:
            setattr(incident_cost, field, update_data[field])

    db_session.commit()
    return incident_cost


def delete(*, db_session, incident_cost_id: int):
    """Deletes an existing incident cost."""
    db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).delete()
    db_session.commit()


def get_engagement_multiplier(participant_role: str):
    """Returns an engagement multiplier for a given incident role."""
    engagement_mappings = {
        ParticipantRoleType.incident_commander: 1,
        ParticipantRoleType.scribe: 0.75,
        ParticipantRoleType.liaison: 0.75,
        ParticipantRoleType.participant: 0.5,
        ParticipantRoleType.reporter: 0.5,
        # ParticipantRoleType.observer: 0, # NOTE: set to 0. It's not used, as we don't calculate cost for participants with observer role
    }

    return engagement_mappings.get(participant_role)


# from dispatch.incident_participant_activity.models import IncidentParticipantActivityRead

# def calculate_incident_cost(*, db_session, incident_cost_model_id: int) -> float:
#     """Calculates the cost of an incident."""
#     incident_cost_model = get_cost_model_by_id(
#         db_session=db_session, incident_cost_model_id=incident_cost_model_id
#     )

#     # aggregate the user activities
#     user_activity = defaultdict(list[IncidentParticipantActivityRead])
#     for activity in incident_cost_model.activities:
#         # TODO(averyl): implement below
#         event_user_activity = activity.event.get_timestamps_for_all_users()

#         # contains the user activity, their timestamps, and duration?
#         # TODO(averyl): I should include the duration points here too...
#         user_activity = {
#             i: user_activity.get(i, []) + event_user_activity.get(i, [])
#             for i in set(user_activity) | set(event_user_activity)
#         }

#     # calculate the level of effort
#     from datetime import datetime

#     # y = {'user': [PluginEventRead()]}
#     # per = PluginEventRead()
#     y = {}
#     timestamp = datetime.now(1)

#     activity = IncidentCostModelActivityCreate()
#     if activity.enabled:
#         y["user"] = [timestamp, activity.response_time_seconds]

#     return


def calculate_incident_cost(
    incident_id: int, db_session: SessionLocal, incident_review=True
) -> int:
    """Calculates the cost of an incident using the incident's cost model."""
    from dispatch.plugin import service as plugin_service
    from dispatch.participant import service as participant_service

    from dispatch.incident_participant_activity.service import (
        create_or_update,
    )
    from dispatch.incident_participant_activity.models import IncidentParticipantActivityCreate

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # move this under cost model
    # Get the cost model. Iterate through all the listed activities we want to record.
    for activity in incident.incident_cost_model.activities:
        # get the plugin event associated with this activity
        plugin_instance = plugin_service.get_active_instance_by_slug(
            db_session=db_session,
            slug=activity.event.plugin.slug,
            project_id=incident.project.id,
        )
        incident_events = {}

        if not plugin_instance:
            raise ValueError(
                f"Cannot fetch cost model activity. Its associated plugin {activity.event.plugin.title} does not exist."
            )

        try:
            # TODO(averyl): fetch all plugin events since last update
            incident_events = plugin_instance.instance.fetch_incident_events(
                db_session=db_session,
                subject=incident,
                events=[activity.event.name],
            )
        except Exception as e:
            log.exception(e)

        # from dispatch.incident_cost_model_activity.models import IncidentCostModelActivity
        # )  # dict{user: (started_at: timestamp, activity)} = plugin_service.get_all_activities(db_session=db_session, activity=activity.id)
        incident_cost = 0
        for message in incident_events["messages"]:
            print(f"new event (message): {str(message)}")

            # get the recorded activities that fall within the update period.
            # this should also handle if previous incidents have been left hanging bc duration isn't over yet.
            # we want to return all incomplete activities..?

            # Calculate the response cost only if we can get the participant's id from the message
            participant_activity = create_or_update(
                db_session=db_session,
                activity_in=IncidentParticipantActivityCreate(
                    cost_model_activity=activity,
                    started_at=datetime.fromtimestamp(float(message["ts"])),
                    participant=ParticipantRead(
                        id=1
                    ),  # message["user"], # TODO(averyl): get the participant from the message
                    incident=incident,
                ),
            )

            if not participant_activity:
                print("failed to create participant activity")

            # we calculate and round up the hourly rate
            if participant_activity:
                hourly_rate = math.ceil(
                    incident.project.annual_employee_cost / incident.project.business_year_hours
                )
                participants_total_response_time_seconds = activity.response_time_seconds
                additional_incident_cost = math.ceil(
                    ((participants_total_response_time_seconds / SECONDS_IN_HOUR)) * hourly_rate
                )

                print(
                    participants_total_response_time_seconds,
                    "/",
                    SECONDS_IN_HOUR,
                    "*",
                    hourly_rate,
                    "=",
                    additional_incident_cost,
                    ", not rounded = ",
                    ((participants_total_response_time_seconds / SECONDS_IN_HOUR)) * hourly_rate,
                )
                incident_cost += additional_incident_cost

        return incident.total_cost + incident_cost

        # calculate the time spent on the activity
        # get last update time
        # if create_or_update resulted in a create:
        #     incident_cost += activity_duration for timed_out incidents with the largest end_at time.
        # if create_or_update resulted in an update:
        #     incident_cost += timedelta between now and last update

        # alternatively. we could create all the participant activities
        # then get all user activities from the last update. Even if duration isn't finished, the ended_at field should be set to the ended_at duration...

    return incident.total_cost


def calculate_incident_response_cost(
    incident_id: int, db_session: SessionLocal, incident_review=True
):
    """Calculates the response cost of a given incident."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participants_total_response_time_seconds = 0
    if incident.incident_cost_model:
        print(
            f"Calculating {incident.name} incident cost with model {incident.incident_cost_model.name}."
        )
        return calculate_incident_cost(
            incident_id=incident_id, db_session=db_session, incident_review=incident_review
        )

    log.info("No incident cost model. Defaulting to classic incident cost model. See (%link)")

    for participant in incident.participants:
        participant_total_roles_time_seconds = 0

        for participant_role in participant.participant_roles:
            if participant_role.role == ParticipantRoleType.observer:
                # skip calculating cost for participants with the observer role
                continue

            if participant_role.activity == 0:
                # skip calculating cost for roles that have no activity
                continue

            participant_role_assumed_at = participant_role.assumed_at

            if incident.status == IncidentStatus.active:
                # we set the renounced_at default time to the current time
                participant_role_renounced_at = datetime.utcnow()

                if participant_role.renounced_at:
                    # the participant left the conversation or got assigned another role
                    # we use the role's renounced_at time
                    participant_role_renounced_at = participant_role.renounced_at
            else:
                # we set the renounced_at default time to the stable_at time
                participant_role_renounced_at = incident.stable_at

                if participant_role.renounced_at:
                    # the participant left the conversation or got assigned another role
                    if participant_role.renounced_at < incident.stable_at:
                        # we use the role's renounced_at time if it happened before the
                        # incident was marked as stable or closed
                        participant_role_renounced_at = participant_role.renounced_at

            # we calculate the time the participant has spent in the incident role
            participant_role_time = participant_role_renounced_at - participant_role_assumed_at

            if participant_role_time.total_seconds() < 0:
                # the participant was added after the incident was marked as stable
                continue

            # we calculate the number of hours the participant has spent in the incident role
            participant_role_time_hours = participant_role_time.total_seconds() / SECONDS_IN_HOUR

            # we make the assumption that participants only spend 8 hours a day working on the incident,
            # if the incident goes past 24hrs
            # TODO(mvilanova): adjust based on incident priority
            if participant_role_time_hours > HOURS_IN_DAY:
                days, hours = divmod(participant_role_time_hours, HOURS_IN_DAY)
                participant_role_time_hours = math.ceil(((days * HOURS_IN_DAY) / 3) + hours)

            # we make the assumption that participants spend more or less time based on their role
            # and we adjust the time spent based on that
            participant_role_time_seconds = int(
                participant_role_time_hours
                * SECONDS_IN_HOUR
                * get_engagement_multiplier(participant_role.role)
            )

            participant_total_roles_time_seconds += participant_role_time_seconds

        participants_total_response_time_seconds += participant_total_roles_time_seconds

    # we calculate the time spent in incident review related activities
    incident_review_hours = 0
    if incident_review:
        num_participants = len(incident.participants)
        incident_review_prep = (
            1  # we make the assumption that it takes an hour to prepare the incident review
        )
        incident_review_meeting = (
            num_participants * 0.5 * 1
        )  # we make the assumption that only half of the incident participants will attend the 1-hour, incident review session
        incident_review_hours = incident_review_prep + incident_review_meeting

    # we calculate and round up the hourly rate
    hourly_rate = math.ceil(
        incident.project.annual_employee_cost / incident.project.business_year_hours
    )

    # we calculate and round up the incident cost
    incident_cost = math.ceil(
        ((participants_total_response_time_seconds / SECONDS_IN_HOUR) + incident_review_hours)
        * hourly_rate
    )

    return incident_cost
