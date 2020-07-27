import logging

from dispatch.database import SessionLocal
from dispatch.event import service as event_service
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType, ParticipantRoleCreate
from dispatch.plugin import service as plugin_service

from .service import get_or_create, get_by_incident_id_and_email


log = logging.getLogger(__name__)


def add_participant(
    user_email: str, incident_id: id, db_session: SessionLocal, role: ParticipantRoleType = None
):
    """Adds a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get or create a new individual
    individual = individual_service.get_or_create(db_session=db_session, email=user_email)

    # We create a role for the participant
    participant_role_in = ParticipantRoleCreate(role=role)
    participant_role = participant_role_service.create(
        db_session=db_session, participant_role_in=participant_role_in
    )

    # We get or create a new participant
    participant = get_or_create(
        db_session=db_session,
        incident_id=incident.id,
        individual_id=individual.id,
        participant_roles=[participant_role],
    )

    individual.participant.append(participant)
    incident.participants.append(participant)

    # We add and commit the changes
    db_session.add(individual)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{individual.name} added to incident with {participant_role.role} role",
        incident_id=incident_id,
    )

    return participant


def remove_participant(user_email: str, incident_id: int, db_session: SessionLocal):
    """Removes a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get information about the individual
    contact_plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")
    individual_info = contact_plugin.instance.get(user_email)
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

    # We make the participant renounce to their active roles
    participant_active_roles = participant_role_service.get_all_active_roles(
        db_session=db_session, participant_id=participant.id
    )
    for participant_active_role in participant_active_roles:
        participant_role_service.renounce_role(
            db_session=db_session, participant_role=participant_active_role
        )

    # We add and commit the changes
    db_session.add(participant)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{participant.individual.name} removed from incident",
        incident_id=incident_id,
    )

    return True


def reactivate_participant(user_email: str, incident_id: int, db_session: SessionLocal):
    """Reactivates a participant."""
    # We load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get information about the individual
    contact_plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")
    individual_info = contact_plugin.instance.get(user_email)
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
    participant_role_in = ParticipantRoleCreate(role=ParticipantRoleType.participant)
    participant_role = participant_role_service.create(
        db_session=db_session, participant_role_in=participant_role_in
    )
    participant.participant_roles.append(participant_role)

    # We add and commit the changes
    db_session.add(participant)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"{individual_fullname} reactivated",
        incident_id=incident_id,
    )

    return True
