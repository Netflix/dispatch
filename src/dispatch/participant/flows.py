import logging
from typing import TypeVar

from dispatch.case.models import Case
from dispatch.database.core import SessionLocal, get_table_name_by_class_instance
from dispatch.event import service as event_service
from dispatch.incident.models import Incident
from dispatch.individual import service as individual_service
from dispatch.participant.models import Participant
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import (
    ParticipantRoleType,
    ParticipantRoleCreate,
)
from dispatch.participant import service as participant_service
from dispatch.service import service as service_service
from dispatch.enums import EventType


log = logging.getLogger(__name__)

Subject = TypeVar("Subject", Case, Incident)


def add_participant(
    user_email: str,
    subject: Subject,
    db_session: SessionLocal,
    service_id: int = None,
    role: ParticipantRoleType = ParticipantRoleType.participant,
) -> Participant:
    """Adds a participant to an incident or a case."""
    # we get or create a new individual
    individual = individual_service.get_or_create(
        db_session=db_session, project=subject.project, email=user_email
    )

    # we get or create a new participant
    subject_type = get_table_name_by_class_instance(subject)
    participant_role = ParticipantRoleCreate(role=role)
    participant = participant_service.get_or_create(
        db_session=db_session,
        subject_id=subject.id,
        subject_type=subject_type,
        individual_id=individual.id,
        service_id=service_id,
        participant_roles=[participant_role],
    )

    individual.participant.append(participant)
    subject.participants.append(participant)

    # TODO: Split this assignment depending on Obj type
    # we update the commander, reporter, scribe, or liaison foreign key
    if role == ParticipantRoleType.incident_commander:
        subject.commander_id = participant.id
        subject.commanders_location = participant.location
    elif role == ParticipantRoleType.reporter:
        subject.reporter_id = participant.id
        subject.reporters_location = participant.location
    elif role == ParticipantRoleType.scribe:
        subject.scribe_id = participant.id
    elif role == ParticipantRoleType.liaison:
        subject.liaison_id = participant.id
    elif role == ParticipantRoleType.observer:
        subject.observer_id = participant.id
    elif role == ParticipantRoleType.assignee:
        subject.assignee_id = participant.id

    # we add and commit the changes
    db_session.add(participant)
    db_session.add(individual)
    db_session.add(subject)
    db_session.commit()

    if subject_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{individual.name} added to case with {participant_role.role} role",
            case_id=subject.id,
        )
    if subject_type == "incident":
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{individual.name} added to incident with {participant_role.role} role",
            incident_id=subject.id,
            type=EventType.participant_updated,
        )

    return participant


def remove_participant(user_email: str, incident: Incident, db_session: SessionLocal):
    """Removes a participant."""
    inactivated = inactivate_participant(user_email, incident, db_session)

    if inactivated:
        participant = participant_service.get_by_incident_id_and_email(
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
            type=EventType.participant_updated,
        )


def remove_case_participant(user_email: str, case: Case, db_session: SessionLocal):
    """Removes a participant."""
    inactivated = inactivate_participant(user_email, case, db_session)

    if inactivated:
        participant = participant_service.get_by_case_id_and_email(
            db_session=db_session, case_id=case.id, email=user_email
        )

        log.debug(f"Removing {participant.individual.name} from {case.name} case...")

        participant.service = None

        db_session.add(participant)
        db_session.commit()

        event_service.log_subject_event(
            subject=case,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{participant.individual.name} has been removed",
            type=EventType.participant_updated,
        )


def inactivate_participant(user_email: str, subject: Subject, db_session: SessionLocal):
    """Inactivates a participant."""
    subject_type = get_table_name_by_class_instance(subject)

    if subject_type == "case":
        participant = participant_service.get_by_case_id_and_email(
            db_session=db_session, case_id=subject.id, email=user_email
        )
    else:
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=subject.id, email=user_email
        )

    if not participant:
        log.debug(
            f"Can't inactivate participant with {user_email} email. They're not a participant of {subject.name} {subject_type}."
        )
        return False

    log.debug(f"Inactivating {participant.individual.name} from {subject.name} {subject_type}...")

    participant_active_roles = participant_role_service.get_all_active_roles(
        db_session=db_session, participant_id=participant.id
    )
    for participant_active_role in participant_active_roles:
        participant_role_service.renounce_role(
            db_session=db_session, participant_role=participant_active_role
        )

    event_service.log_subject_event(
        subject=subject,
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{participant.individual.name} has been inactivated",
        type=EventType.participant_updated,
    )
    return True


def reactivate_participant(
    user_email: str, incident: Incident, db_session: SessionLocal, service_id: int = None
):
    """Reactivates a participant."""
    participant = participant_service.get_by_incident_id_and_email(
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
        type=EventType.participant_updated,
    )

    return True
