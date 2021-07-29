from datetime import datetime
from typing import List, Optional

from dispatch.participant import service as participant_service

from .models import (
    ParticipantRole,
    ParticipantRoleType,
    ParticipantRoleCreate,
    ParticipantRoleUpdate,
)


def get(*, db_session, participant_role_id: int) -> Optional[ParticipantRole]:
    """Returns a participant role based on the given id."""
    return (
        db_session.query(ParticipantRole).filter(ParticipantRole.id == participant_role_id).first()
    )


def get_last_active_role(
    *,
    db_session,
    participant_id: int,
) -> Optional[ParticipantRole]:
    """Returns the participant's last active role."""
    return (
        db_session.query(ParticipantRole)
        .filter(ParticipantRole.participant_id == participant_id)
        .order_by(ParticipantRole.renounced_at.desc())
        .first()
    )


def get_all_active_roles(*, db_session, participant_id: int) -> List[Optional[ParticipantRole]]:
    """Returns all active roles for the given participant id."""
    return (
        db_session.query(ParticipantRole)
        .filter(ParticipantRole.participant_id == participant_id)
        .filter(ParticipantRole.renounced_at.is_(None))
    )


def get_all(*, db_session):
    """Returns all participant roles."""
    return db_session.query(ParticipantRole)


def add_role(
    *, db_session, participant_id: int, participant_role: ParticipantRoleType
) -> ParticipantRole:
    """Adds a role to a participant."""
    participant = participant_service.get(db_session=db_session, participant_id=participant_id)
    participant_role_in = ParticipantRoleCreate(role=participant_role)
    participant_role = create(db_session=db_session, participant_role_in=participant_role_in)
    participant.participant_roles.append(participant_role)
    db_session.add(participant)
    db_session.commit()
    return participant_role


def renounce_role(*, db_session, participant_role: ParticipantRole) -> ParticipantRole:
    """Renounces the given role."""
    participant_role.renounced_at = datetime.utcnow()
    db_session.add(participant_role)
    db_session.commit()
    return participant_role


def create(*, db_session, participant_role_in: ParticipantRoleCreate) -> ParticipantRole:
    """Creates a new participant role."""
    participant_role = ParticipantRole(**participant_role_in.dict())
    db_session.add(participant_role)
    db_session.commit()
    return participant_role


def update(
    *, db_session, participant_role: ParticipantRole, participant_role_in: ParticipantRoleUpdate
) -> ParticipantRole:
    """Updates a participant role."""
    participant_role_data = participant_role.dict()

    update_data = participant_role_in.dict(skip_defaults=True)

    for field in participant_role_data:
        if field in update_data:
            setattr(participant_role, field, update_data[field])

    db_session.commit()
    return participant_role


def delete(*, db_session, participant_role_id: int):
    """Deletes a participant role."""
    participant_role = (
        db_session.query(ParticipantRole).filter(ParticipantRole.id == participant_role_id).first()
    )
    db_session.delete(participant_role)
    db_session.commit()
