from datetime import datetime

from typing import Optional

from .models import ParticipantRole, ParticipantRoleType


def get(*, db_session, participant_role_id: int) -> Optional[ParticipantRole]:
    return (
        db_session.query(ParticipantRole).filter(ParticipantRole.id == participant_role_id).first()
    )


def get_active_roles(*, db_session, participant_id: int) -> Optional[ParticipantRole]:
    """Gets the participant's active roles by participant id."""
    return (
        db_session.query(ParticipantRole)
        .filter(ParticipantRole.participant_id == participant_id)
        .filter(ParticipantRole.renounce_at.is_(None))
    )


def renounce_role(
    *, db_session, participant_id: int, role_type: str = ParticipantRoleType.participant
) -> Optional[ParticipantRole]:
    """Renounces the given role."""
    participant_roles = get_active_roles(db_session=db_session, participant_id=participant_id)
    for pr in participant_roles:
        if pr.role == role_type:
            pr.renounce_at = datetime.utcnow()
            break
    return pr


def get_all(*, db_session):
    return db_session.query(ParticipantRole)


def create(*, db_session, **kwargs) -> ParticipantRole:
    participant_role = ParticipantRole(**kwargs)
    db_session.add(participant_role)
    db_session.commit()
    return participant_role
