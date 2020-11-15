import math
from datetime import datetime, timedelta
from typing import List, Optional


from dispatch.config import ANNUAL_COST_EMPLOYEE, BUSINESS_HOURS_YEAR
from dispatch.database import SessionLocal
from dispatch.event import service as event_service
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.participant import flows as participant_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import TagCreate
from dispatch.term import service as term_service
from dispatch.term.models import TermUpdate

from .enums import IncidentStatus
from .models import Incident, IncidentUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600


def assign_incident_role(
    db_session: SessionLocal,
    incident: Incident,
    reporter_email: str,
    role: ParticipantRoleType,
):
    """Assigns incident roles."""
    # We resolve the incident role email
    # default to reporter if we don't have an oncall plugin enabled
    assignee_email = reporter_email

    oncall_plugin = plugin_service.get_active(db_session=db_session, plugin_type="oncall")
    if not oncall_plugin:
        assignee_email = reporter_email

        # Add a new participant (duplicate participants with different roles will be updated)
        participant_flows.add_participant(
            assignee_email,
            incident.id,
            db_session,
            role,
        )
        return

    if role == ParticipantRoleType.incident_commander:
        # default to reporter
        if incident.incident_type.commander_service:
            service = incident.incident_type.commander_service
            assignee_email = oncall_plugin.instance.get(service_id=service.external_id)
            if incident.incident_priority.page_commander:
                oncall_plugin.instance.page(
                    service_id=service.external_id,
                    incident_name=incident.name,
                    incident_title=incident.title,
                    incident_description=incident.description,
                )
    else:
        if incident.incident_type.liaison_service:
            service = incident.incident_type.liaison_service
            assignee_email = oncall_plugin.instance.get(service_id=service.external_id)

    # Add a new participant (duplicate participants with different roles will be updated)
    participant_flows.add_participant(
        assignee_email,
        incident.id,
        db_session,
        role,
    )


def get(*, db_session, incident_id: int) -> Optional[Incident]:
    """Returns an incident based on the given id."""
    return db_session.query(Incident).filter(Incident.id == incident_id).first()


def get_by_name(*, db_session, incident_name: str) -> Optional[Incident]:
    """Returns an incident based on the given name."""
    return db_session.query(Incident).filter(Incident.name == incident_name).first()


def get_all(*, db_session) -> List[Optional[Incident]]:
    """Returns all incidents."""
    return db_session.query(Incident)


def get_all_by_status(
    *, db_session, status: IncidentStatus, skip=0, limit=100
) -> List[Optional[Incident]]:
    """Returns all incidents based on the given status."""
    return (
        db_session.query(Incident).filter(Incident.status == status).offset(skip).limit(limit).all()
    )


def get_all_last_x_hours_by_status(
    *, db_session, status: IncidentStatus, hours: int, skip=0, limit=100
) -> List[Optional[Incident]]:
    """Returns all incidents of a given status in the last x hours."""
    now = datetime.utcnow()

    if status == IncidentStatus.active:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.active)
            .filter(Incident.created_at >= now - timedelta(hours=hours))
            .offset(skip)
            .limit(limit)
            .all()
        )

    if status == IncidentStatus.stable:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.stable)
            .filter(Incident.stable_at >= now - timedelta(hours=hours))
            .offset(skip)
            .limit(limit)
            .all()
        )

    if status == IncidentStatus.closed:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.closed)
            .filter(Incident.closed_at >= now - timedelta(hours=hours))
            .offset(skip)
            .limit(limit)
            .all()
        )


def get_all_by_incident_type(
    *, db_session, incident_type: str, skip=0, limit=100
) -> List[Optional[Incident]]:
    """Returns all incidents with the given incident type."""
    return (
        db_session.query(Incident)
        .filter(Incident.incident_type.name == incident_type)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    *,
    db_session,
    incident_priority: str,
    incident_type: str,
    reporter_email: str,
    title: str,
    status: str,
    description: str,
    tags: List[dict],
    visibility: str = None,
) -> Incident:
    """Creates a new incident."""
    # We get the incident type by name
    if not incident_type:
        incident_type = incident_type_service.get_default(db_session=db_session)
        if not incident_type:
            raise Exception("No incident type specified and no default has been defined.")
    else:
        incident_type = incident_type_service.get_by_name(
            db_session=db_session, name=incident_type["name"]
        )

    # We get the incident priority by name
    if not incident_priority:
        incident_priority = incident_priority_service.get_default(db_session=db_session)
        if not incident_priority:
            raise Exception("No incident priority specified and no default has been defined.")
    else:
        incident_priority = incident_priority_service.get_by_name(
            db_session=db_session, name=incident_priority["name"]
        )

    if not visibility:
        visibility = incident_type.visibility

    tag_objs = []
    for t in tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=TagCreate(**t)))

    # We create the incident
    incident = Incident(
        title=title,
        description=description,
        status=status,
        incident_type=incident_type,
        incident_priority=incident_priority,
        visibility=visibility,
        tags=tag_objs,
    )
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident created",
        incident_id=incident.id,
    )

    # We add the reporter to the incident
    participant_flows.add_participant(
        reporter_email, incident.id, db_session, ParticipantRoleType.reporter
    )

    # Add other incident roles (e.g. commander and liaison)
    assign_incident_role(
        db_session, incident, reporter_email, ParticipantRoleType.incident_commander
    )
    assign_incident_role(db_session, incident, reporter_email, ParticipantRoleType.liaison)

    return incident


def update(*, db_session, incident: Incident, incident_in: IncidentUpdate) -> Incident:
    incident_priority = incident_priority_service.get_by_name(
        db_session=db_session, name=incident_in.incident_priority.name
    )

    incident_type = incident_type_service.get_by_name(
        db_session=db_session, name=incident_in.incident_type.name
    )

    tags = []
    for t in incident_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=TagCreate(**t)))

    terms = []
    for t in incident_in.terms:
        terms.append(term_service.get_or_create(db_session=db_session, term_in=TermUpdate(**t)))

    duplicates = []
    for d in incident_in.duplicates:
        duplicates.append(get(db_session=db_session, incident_id=d.id))

    update_data = incident_in.dict(
        skip_defaults=True,
        exclude={
            "incident_type",
            "incident_priority",
            "commander",
            "reporter",
            "status",
            "visibility",
            "tags",
            "terms",
            "duplicates",
        },
    )

    for field in update_data.keys():
        setattr(incident, field, update_data[field])

    incident.terms = terms
    incident.tags = tags
    incident.duplicates = duplicates

    incident.status = incident_in.status
    incident.visibility = incident_in.visibility

    incident.incident_priority = incident_priority
    incident.incident_type = incident_type

    db_session.add(incident)
    db_session.commit()

    return incident


def delete(*, db_session, incident_id: int):
    # TODO: When deleting, respect referential integrity here in the code. Or add cascading deletes
    # in models.py.
    db_session.query(Incident).filter(Incident.id == incident_id).delete()
    db_session.commit()


def get_engagement_multiplier(participant_role: str):
    """Returns an engagement multiplier for a given incident role."""
    engagement_mappings = {
        ParticipantRoleType.incident_commander: 1,
        ParticipantRoleType.scribe: 0.75,
        ParticipantRoleType.liaison: 0.75,
        ParticipantRoleType.participant: 0.5,
        ParticipantRoleType.reporter: 0.5,
    }

    return engagement_mappings.get(participant_role)


def calculate_cost(incident_id: int, db_session: SessionLocal, incident_review=True):
    """Calculates the cost of a given incident."""
    incident = get(db_session=db_session, incident_id=incident_id)

    participants_total_response_time_seconds = 0
    for participant in incident.participants:

        participant_total_roles_time_seconds = 0
        for participant_role in participant.participant_roles:
            # TODO(mvilanova): skip if we did not see activity from the participant in the incident conversation

            participant_role_assumed_at = participant_role.assumed_at

            if incident.status == IncidentStatus.active.value:
                # the incident is still active. we use the current time
                participant_role_renounced_at = datetime.utcnow()
            else:
                # the incident is stable or closed. we use the stable_at time
                participant_role_renounced_at = incident.stable_at

            if participant_role.renounced_at:
                # the participant left the conversation or got assigned another role
                # we use the renounced_at time
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
    hourly_rate = math.ceil(ANNUAL_COST_EMPLOYEE / BUSINESS_HOURS_YEAR)

    # we calculate and round up the incident cost
    incident_cost = math.ceil(
        ((participants_total_response_time_seconds / SECONDS_IN_HOUR) + incident_review_hours)
        * hourly_rate
    )

    return incident_cost
