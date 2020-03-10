from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.individual.models import IndividualContact
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRole, ParticipantRoleType

from .models import Participant, ParticipantCreate, ParticipantUpdate


def get(*, db_session, participant_id: int) -> Optional[Participant]:
    """
    Get a participant by id.
    """
    return db_session.query(Participant).filter(Participant.id == participant_id).first()


def get_by_individual_contact_id(
    *, db_session, individual_contact_id: int
) -> Optional[Participant]:
    """
    Get a participant by individual contact id.
    """
    return (
        db_session.query(Participant)
        .filter(Participant.individual_contact_id == individual_contact_id)
        .first()
    )


def get_by_incident_id_and_role(
    *, db_session, incident_id: int, role: str
) -> Optional[Participant]:
    """
    Get a participant by incident id and role name.
    """
    return (
        db_session.query(Participant)
        .filter(Participant.incident_id == incident_id)
        .join(ParticipantRole)
        .filter(ParticipantRole.renounce_at.is_(None))
        .filter(ParticipantRole.role == role)
        .one_or_none()
    )


def get_by_incident_id_and_email(
    *, db_session, incident_id: int, email: str
) -> Optional[Participant]:
    """
    Get a participant by incident id and email.
    """
    return (
        db_session.query(Participant)
        .filter(Participant.incident_id == incident_id)
        .join(IndividualContact)
        .filter(IndividualContact.email == email)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[Participant]]:
    """
    Get all participants.
    """
    return db_session.query(Participant)


def get_all_by_incident_id(*, db_session, incident_id: int) -> List[Optional[Participant]]:
    """Get all participants by incident id."""
    return db_session.query(Participant).filter(Participant.incident_id == incident_id)


def get_or_create(
    *,
    db_session,
    incident_id: int,
    individual_id: int,
    participant_roles: List[ParticipantRoleType],
) -> Participant:
    """Gets an existing participant object or creates a new one."""
    participant = (
        db_session.query(Participant)
        .filter(Participant.incident_id == incident_id)
        .filter(Participant.individual_contact_id == individual_id)
        .one_or_none()
    )

    if not participant:
        participant_in = ParticipantCreate(participant_role=participant_roles)
        participant = create(db_session=db_session, participant_in=participant_in)

    return participant


def create(*, db_session, participant_in: ParticipantCreate) -> Participant:
    """
    Create a new participant.
    """
    participant_roles = [
        participant_role_service.create(db_session=db_session, participant_role_in=participant_role)
        for participant_role in participant_in.participant_role
    ]
    participant = Participant(
        **participant_in.dict(exclude={"participant_role"}), participant_role=participant_roles
    )
    db_session.add(participant)
    db_session.commit()
    return participant


def create_all(*, db_session, participants_in: List[ParticipantCreate]) -> List[Participant]:
    """
    Create a list of participants.
    """
    participants = [Participant(**t.dict()) for t in participants_in]
    db_session.bulk_save_objects(participants)
    db_session.commit()
    return participants


def update(
    *, db_session, participant: Participant, participant_in: ParticipantUpdate
) -> Participant:
    """
    Updates a participant.
    """
    participant_data = jsonable_encoder(participant)

    update_data = participant_in.dict(skip_defaults=True)

    for field in participant_data:
        if field in update_data:
            setattr(participant, field, update_data[field])

    db_session.add(participant)
    db_session.commit()
    return participant


def delete(*, db_session, participant_id: int):
    """
    Deletes a participant.
    """
    participant = db_session.query(Participant).filter(Participant.id == participant_id).first()
    db_session.delete(participant)
    db_session.commit()
