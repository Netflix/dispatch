import logging

from dispatch.database import SessionLocal
from dispatch.incident.models import Incident
from dispatch.participant import service as participant_service

from .models import ParticipantRoleType, ParticipantRoleCreate
from .service import create, get_all_active_roles, renounce_role

log = logging.getLogger(__name__)


def assign_role_flow(
    db_session: SessionLocal, incident: Incident, assignee_contact_info: dict, assignee_role: str
):
    """Attempts to assign a role to a participant.

    Returns:
        str:
        - "role_assigned", if role assigned.
        - "role_not_assigned", if not role assigned.
        - "assignee_has_role", if assignee already has the role.

    """
    # we get the participant that holds the role assigned to the assignee
    participant_with_assignee_role = participant_service.get_by_incident_id_and_role(
        db_session=db_session, incident_id=incident.id, role=assignee_role
    )

    # we get the participant for the assignee
    assignee_participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=assignee_contact_info["email"]
    )

    if participant_with_assignee_role is assignee_participant:
        return "assignee_has_role"

    if participant_with_assignee_role:
        # we make them renounce to the role that was assigned to the assignee
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=participant_with_assignee_role.id
        )
        for participant_active_role in participant_active_roles:
            if participant_active_role.role == assignee_role:
                renounce_role(db_session=db_session, participant_role=participant_active_role)

        # we create a new role for the participant
        participant_role_in = ParticipantRoleCreate(role=ParticipantRoleType.participant)
        participant_role = create(db_session=db_session, participant_role_in=participant_role_in)

        # we assign the new role to the participant
        participant_with_assignee_role.participant_role.append(participant_role)

        # we commit the changes to the database
        db_session.add(participant_with_assignee_role)
        db_session.commit()

        log.debug(
            f"We made {participant_with_assignee_role.individual.name} renounce to the {assignee_role} role."
        )

    if assignee_participant:
        # we make the assignee renounce to their current role
        participant_active_roles = get_all_active_roles(
            db_session=db_session, participant_id=assignee_participant.id
        )

        for participant_active_role in participant_active_roles:
            if participant_active_role.role != ParticipantRoleType.reporter:
                renounce_role(db_session=db_session, participant_role=participant_active_role)

        # we create a new role for the assignee
        participant_role_in = ParticipantRoleCreate(role=assignee_role)
        assignee_participant_role = create(
            db_session=db_session, participant_role_in=participant_role_in
        )

        # we assign the new role to the assignee
        assignee_participant.participant_role.append(assignee_participant_role)

        # we commit the changes to the database
        db_session.add(assignee_participant)
        db_session.commit()

        log.debug(f"We assigned the {assignee_role} role to {assignee_contact_info['fullname']}.")

        return "role_assigned"

    log.debug(
        f"We were not able to assign the {assignee_role} role to {assignee_contact_info['fullname']}."
    )

    return "role_not_assigned"
