import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dispatch.models import Incident

from dispatch.database.core import Session, SessionLocal, get_table_name_by_class_instance
from dispatch.event import service as event_service
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import (
    ParticipantRoleType,
    ParticipantRoleUpdate,
)
from .service import get_all_active_roles, add_role, renounce_role


log = logging.getLogger(__name__)


def assign_role_flow(
    incident: "Incident", assignee_email: str, assignee_role: str, db_session: SessionLocal
):
    """Attempts to assign a role to a participant.

    Returns:
        str:
        - "role_assigned", if role assigned.
        - "role_not_assigned", if not role assigned.
        - "assignee_has_role", if assignee already has the role.

    """
    # we get the participant for the assignee
    assignee_participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=assignee_email
    )

    if assignee_role == ParticipantRoleType.observer:
        # we make the assignee renounce to the participant role
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=assignee_participant.id
        )
        for participant_active_role in participant_active_roles:
            if participant_active_role.role == ParticipantRoleType.participant:
                renounce_role(db_session=db_session, participant_role=participant_active_role)
                break

        # we give the assignee the new role
        add_role(
            db_session=db_session,
            participant_id=assignee_participant.id,
            participant_role=assignee_role,
        )

        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{assignee_participant.individual.name} has been assigned the role of {assignee_role}",
            incident_id=incident.id,
        )

        return "role_assigned"

    # we get the participant that holds the role assigned to the assignee
    participant_with_assignee_role = participant_service.get_by_incident_id_and_role(
        db_session=db_session, incident_id=incident.id, role=assignee_role
    )

    if participant_with_assignee_role is assignee_participant:
        return "assignee_has_role"

    if participant_with_assignee_role:
        # we make the participant renounce to the role that has been given to the assignee
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=participant_with_assignee_role.id
        )
        for participant_active_role in participant_active_roles:
            if participant_active_role.role == assignee_role:
                renounce_role(db_session=db_session, participant_role=participant_active_role)
                break

        # we check if the participant has other active roles
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=participant_with_assignee_role.id
        )
        if participant_active_roles.count() == 0:
            # we give the participant a new participant role
            add_role(
                db_session=db_session,
                participant_id=participant_with_assignee_role.id,
                participant_role=ParticipantRoleType.participant,
            )

        log.debug(
            f"We made {participant_with_assignee_role.individual.name} renounce to their {assignee_role} role."
        )

    if assignee_participant:
        # we make the assignee renounce to the participant role, if they have it
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=assignee_participant.id
        )
        for participant_active_role in participant_active_roles:
            if participant_active_role.role == ParticipantRoleType.participant:
                renounce_role(db_session=db_session, participant_role=participant_active_role)
                break

        # we give the assignee the new role
        add_role(
            db_session=db_session,
            participant_id=assignee_participant.id,
            participant_role=assignee_role,
        )

        # we update the commander, reporter, scribe, or liaison foreign key
        if assignee_role == ParticipantRoleType.incident_commander:
            incident.commander_id = assignee_participant.id
        elif assignee_role == ParticipantRoleType.reporter:
            incident.reporter_id = assignee_participant.id
        elif assignee_role == ParticipantRoleType.scribe:
            incident.scribe_id = assignee_participant.id
        elif assignee_role == ParticipantRoleType.liaison:
            incident.liaison_id = assignee_participant.id

        # we add and commit the changes
        db_session.add(incident)
        db_session.commit()

        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{assignee_participant.individual.name} has been assigned the role of {assignee_role}",
            incident_id=incident.id,
        )

        return "role_assigned"

    log.debug(f"We were not able to assign the {assignee_role} role to {assignee_email}.")

    return "role_not_assigned"


def change_role_flow(
    db_session: Session,
    subject: Any,
    user_email: str,
    from_role: ParticipantRoleType,
    to_role: ParticipantRoleType = ParticipantRoleType.participant,
):
    """Changes a participants role."""
    subject_type = get_table_name_by_class_instance(subject)
    if subject_type == "case":
        participant = participant_service.get_by_case_id_and_email(
            db_session=db_session,
            case_id=subject.id,
            email=user_email,
        )
    if subject_type == "incident":
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session,
            incident_id=subject.id,
            email=user_email,
        )

    log.debug(f"Changing {participant.individual.name}'s role from {from_role} to {to_role}...")

    participant_roles = [r.role for r in participant.participant_roles]
    if from_role not in participant_roles:
        log.debug(
            f"{participant.individual.name}'s does not have the role {from_role} that was set to be changed."
        )
        return

    for role in participant.participant_roles:
        if from_role == role.role:
            from_participant_role = role

    log.debug(f"{participant.individual.name}'s role changed from {from_role} to {to_role}...")

    participant_role_in = ParticipantRoleUpdate(role=to_role)
    participant_role_service.update(
        db_session=db_session,
        participant_role=from_participant_role,
        participant_role_in=participant_role_in,
    )
