import logging
from typing import TypeVar

from dispatch.case.models import Case
from dispatch.database.core import SessionLocal, get_table_name_by_class_instance
from dispatch.event import service as event_service
from dispatch.incident.models import Incident
from dispatch.individual import service as individual_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType, ParticipantRoleCreate
from dispatch.service import service as service_service

from .service import get_or_create, get_by_incident_id_and_email


log = logging.getLogger(__name__)

Obj = TypeVar("Obj", Case, Incident)


def add_participant(
    user_email: str,
    obj: Obj,
    db_session: SessionLocal,
    service_id: int = None,
    role: ParticipantRoleType = ParticipantRoleType.participant,
):
    """Adds a participant."""

    # we get or create a new individual
    individual = individual_service.get_or_create(
        db_session=db_session, incident=obj, email=user_email
    )

    # we get or create a new participant
    obj_type = get_table_name_by_class_instance(obj)
    participant_role = ParticipantRoleCreate(role=role)
    participant = get_or_create(
        db_session=db_session,
        obj_id=obj.id,
        obj_type=obj_type,
        individual_id=individual.id,
        service_id=service_id,
        participant_roles=[participant_role],
    )

    individual.participant.append(participant)
    obj.participants.append(participant)

    # TODO: Split this assignment depending on Obj type
    # we update the commander, reporter, scribe, or liaison foreign key
    if role == ParticipantRoleType.incident_commander:
        obj.commander_id = participant.id
        obj.commanders_location = participant.location
    elif role == ParticipantRoleType.reporter:
        obj.reporter_id = participant.id
        obj.reporters_location = participant.location
    elif role == ParticipantRoleType.scribe:
        obj.scribe_id = participant.id
    elif role == ParticipantRoleType.liaison:
        obj.liaison_id = participant.id
    elif role == ParticipantRoleType.observer:
        obj.observer_id = participant.id

    # we add and commit the changes
    db_session.add(participant)
    db_session.add(individual)
    db_session.add(obj)
    db_session.commit()

    if obj_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description="Case group updated",
            case_id=obj.id,
        )
    if obj_type == "incident":
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description="Incident group updated",
            incident_id=obj.id,
        )

    print("LOG: END PARTICIPANT CREATE FLOW")
    return participant


def remove_participant(user_email: str, incident: Incident, db_session: SessionLocal):
    """Removes a participant."""
    inactivated = inactivate_participant(user_email, incident, db_session)

    if inactivated:
        participant = get_by_incident_id_and_email(
            db_session=db_session, incident_id=incident.id, email=user_email
        )

        log.debug(f"Removing {participant.individual.name} from {incident.name} incident...")

        participant.service = None

        db_session.add(participant)
        db_session.commit()

        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{participant.individual.name} has been removed",
            incident_id=incident.id,
        )


def inactivate_participant(user_email: str, incident: Incident, db_session: SessionLocal):
    """Inactivates a participant."""
    participant = get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    if not participant:
        log.debug(
            f"Can't inactivate participant with {user_email} email. They're not a participant of {incident.name} incident."
        )
        return False

    log.debug(f"Inactivating {participant.individual.name} from {incident.name} incident...")

    participant_active_roles = participant_role_service.get_all_active_roles(
        db_session=db_session, participant_id=participant.id
    )
    for participant_active_role in participant_active_roles:
        participant_role_service.renounce_role(
            db_session=db_session, participant_role=participant_active_role
        )

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{participant.individual.name} has been inactivated",
        incident_id=incident.id,
    )

    return True


def reactivate_participant(
    user_email: str, incident: Incident, db_session: SessionLocal, service_id: int = None
):
    """Reactivates a participant."""
    participant = get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    if not participant:
        log.debug(f"{user_email} is not an inactive participant of {incident.name} incident.")
        return False

    log.debug(f"Reactivating {participant.individual.name} on {incident.name} incident...")

    # we get the last active role
    participant_role = participant_role_service.get_last_active_role(
        db_session=db_session, participant_id=participant.id
    )
    # we create a new role based on the last active role
    participant_role_in = ParticipantRoleCreate(role=participant_role.role)
    participant_role = participant_role_service.create(
        db_session=db_session, participant_role_in=participant_role_in
    )
    participant.participant_roles.append(participant_role)

    if service_id:
        service = service_service.get(db_session=db_session, service_id=service_id)
        participant.service = service

    db_session.add(participant)
    db_session.commit()

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{participant.individual.name} has been reactivated",
        incident_id=incident.id,
    )

    return True
