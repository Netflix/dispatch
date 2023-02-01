"""empty message

Revision ID: c1aa5f8ceeeb
Revises: e4b4991dddcd
Create Date: 2023-02-01 10:56:46.681543

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm import Session
from dispatch.case.models import Case
from dispatch.participant import flows as participant_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.auth.models import DispatchUser
from dispatch.participant import service as participant_service

# revision identifiers, used by Alembic.
revision = "c1aa5f8ceeeb"
down_revision = "e4b4991dddcd"
branch_labels = None
depends_on = None


def upgrade():
    print("Migrating case assignees to Participant from DispatchUser..")

    bind = op.get_bind()
    session = Session(bind=bind)

    cases: list[Case] = session.query(Case).all()

    for case in cases:
        participant = participant_service.get(db_session=session, participant_id=case.assignee_id)
        if participant is None and case.assignee is not None:
            assignee: DispatchUser = case.assignee

            participant = participant_flows.add_participant(
                user_email=assignee.email,
                subject=case,
                db_session=session,
                role=ParticipantRoleType.assignee,
            )
            case.assignee_id = participant.id
            participant.case_id = case.id
    session.commit()

    print("Case assignees migrated from DispatchUser to Participant..")


def downgrade():
    pass
