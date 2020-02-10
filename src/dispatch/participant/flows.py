import logging

from dispatch.config import INCIDENT_CONTACT_PLUGIN_SLUG
from dispatch.database import SessionLocal
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins

from .service import get_or_create, get_by_incident_id_and_email


log = logging.getLogger(__name__)


def add_participant(
    user_email: str, incident_id: id, db_session: SessionLocal, role: ParticipantRoleType = None
):
    """Adds a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We add the participant to the incident
    individual = individual_service.get_or_create(db_session=db_session, email=user_email)

    participant_role = participant_role_service.create(db_session=db_session, role=role)
    participant = get_or_create(
        db_session=db_session,
        incident_id=incident.id,
        individual_id=individual.id,
        role=participant_role,
    )

    individual.participant.append(participant)
    incident.participants.append(participant)

    # We add and commit the changes
    db_session.add(individual)
    db_session.add(incident)
    db_session.commit()

    log.debug(f"{individual.name} has been added to incident {incident.name}.")

    return True


def remove_participant(user_email: str, incident_id: int, db_session: SessionLocal):
    """Removes a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get information about the individual
    contact_plugin = plugins.get(INCIDENT_CONTACT_PLUGIN_SLUG)
    individual_info = contact_plugin.get(user_email)
    individual_fullname = individual_info["fullname"]

    log.debug(f"Removing {individual_fullname} from incident {incident.name}...")

    participant = get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    if not participant:
        log.debug(
            f"Can't remove {individual_fullname}. They're not an active participant of incident {incident.name}."
        )
        return False

    # We mark the participant as inactive
    participant.is_active = False

    # We make the participant renouce to their active roles
    participant_active_roles = participant_role_service.get_active_roles(
        db_session=db_session, participant_id=participant.id
    )

    for active_role in participant_active_roles:
        participant_role_service.renounce_role(
            db_session=db_session, participant_id=participant.id, role_type=active_role.role
        )

    # We add and commit the changes
    db_session.add(participant)
    db_session.commit()

    log.debug(f"Participant {participant.individual.name} has been removed from the incident.")

    return True


def reactivate_participant(user_email: str, incident_id: int, db_session: SessionLocal):
    """Reactivates a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get information about the individual
    contact_plugin = plugins.get(INCIDENT_CONTACT_PLUGIN_SLUG)
    individual_info = contact_plugin.get(user_email)
    individual_fullname = individual_info["fullname"]

    log.debug(f"Reactivating {individual_fullname} on incident {incident.name}...")

    participant = get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    if not participant:
        log.debug(
            f"{individual_fullname} is not an inactive participant of incident {incident.name}."
        )
        return False

    # We mark the participant as active
    participant.is_active = True

    # We create a role for the participant
    participant_role = participant_role_service.create(db_session=db_session)
    participant.participant_role.append(participant_role)

    # We add and commit the changes
    db_session.add(participant)
    db_session.commit()

    log.debug(f"{individual_fullname} has been reactivated.")

    return True
