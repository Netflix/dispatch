"""empty message

Revision ID: e4b4991dddcd
Revises: 956eb8f8987e
Create Date: 2023-01-30 10:52:31.676368

"""
from alembic import op

from enum import Enum
from pydantic import ConfigDict, BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.expression import true
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = "e4b4991dddcd"
down_revision = "956eb8f8987e"
branch_labels = None
depends_on = None


Base = declarative_base()


class DispatchUser(Base):
    __tablename__ = "dispatch_user"
    __table_args__ = {"schema": "dispatch_core"}
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String)


class Project(Base):
    __tablename__ = "project"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    default = sa.Column(sa.Boolean, default=False)


class Case(Base):
    __tablename__ = "case"
    id = sa.Column(sa.Integer, primary_key=True)

    assignee_id = sa.Column(sa.Integer, sa.ForeignKey(DispatchUser.id))
    _assignee_id = sa.Column(sa.Integer, sa.ForeignKey("participant.id"))


# Pydantic models...
class DispatchBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True, arbitrary_types_allowed=True, str_strip_whitespace=True)


class DispatchEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class ParticipantRole(Base):
    __tablename__ = "participant_role"
    id = sa.Column(sa.Integer, primary_key=True)
    role = sa.Column(sa.String)


class ParticipantRoleBase(DispatchBase):
    role: str


class ParticipantRoleType(DispatchEnum):
    assignee = "Assignee"
    reporter = "Reporter"


class ParticipantRoleCreate(ParticipantRoleBase):
    role: ParticipantRoleType | None = None


class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return sa.Column(sa.Integer, sa.ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):  # noqa
        return relationship("Project")


class IndividualContact(Base, ProjectMixin):
    __tablename__ = "individual_contact"

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String)
    name = sa.Column(sa.String)
    weblink = sa.Column(sa.String)


class Participant(Base):
    __tablename__ = "participant"
    id = sa.Column(sa.Integer, primary_key=True)
    case_id = sa.Column(sa.Integer)
    individual_contact_id = sa.Column(sa.Integer)


def is_participant(db_session: Session, participant_id: int) -> bool:
    return (
        True
        if db_session.query(Participant).filter(Participant.id == participant_id).first()
        is not None
        else False
    )


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "case",
        sa.Column("participants_team", sa.String()),
    )
    op.add_column(
        "case",
        sa.Column("participants_location", sa.String()),
    )
    op.add_column(
        "case",
        sa.Column("_assignee_id", sa.Integer()),
    )
    op.add_column(
        "participant",
        sa.Column("case_id", sa.Integer()),
    )

    print("Migrating case assignees to Participant from DispatchUser..")

    bind = op.get_bind()
    db_session = Session(bind=bind)

    for case in db_session.query(Case):
        print(f"Processing Case {case.id}...")
        if not is_participant(db_session, participant_id=case.assignee_id):
            current_user = (
                db_session.query(DispatchUser).filter(DispatchUser.id == case.assignee_id).first()
            )
            individual = (
                db_session.query(IndividualContact)
                .filter(IndividualContact.email == current_user.email)
                .first()
            )
            if individual is None:
                i = {}
                i["email"] = current_user.email
                i["name"] = current_user.email
                i["weblink"] = ""
                default_project = (
                    db_session.query(Project).filter(Project.default == true()).one_or_none()
                )
                individual = IndividualContact(
                    **i,
                    project=default_project if default_project else "default",
                )
                db_session.add(individual)

            participant = Participant(
                individual_contact_id=individual.id,
            )
            db_session.add(participant)
            db_session.commit()
            role = ParticipantRole(role=ParticipantRoleType.assignee)
            participant.participant_roles = role

            case._assignee_id = participant.id
            participant.case_id = case.id
            participant.individual_contact_id = individual.id

    db_session.commit()

    op.create_foreign_key(
        None, "participant", "case", ["case_id"], ["id"], ondelete="CASCADE", use_alter=True
    )
    op.drop_column("case", "assignee_id")
    op.alter_column("case", "_assignee_id", new_column_name="assignee_id")
    op.create_foreign_key(None, "case", "participant", ["assignee_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "participant", type_="foreignkey")
    op.drop_column("participant", "case_id")
    op.drop_constraint(None, "case", type_="foreignkey")
    op.create_foreign_key(
        "case_assignee_id_fkey",
        "case",
        "dispatch_user",
        ["assignee_id"],
        ["id"],
        referent_schema="dispatch_core",
    )
    op.drop_column("case", "participants_location")
    op.drop_column("case", "participants_team")


# ### end Alembic commands ###
