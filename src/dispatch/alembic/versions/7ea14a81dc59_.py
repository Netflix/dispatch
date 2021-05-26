"""Adds organization and project tables.

Revision ID: 7ea14a81dc59
Revises: a769ea6bad64
Create Date: 2021-03-22 12:10:55.316560

"""
from enum import Enum

from alembic import op
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship, Session
from sqlalchemy_utils import TSVectorType

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# revision identifiers, used by Alembic.
revision = "7ea14a81dc59"
down_revision = "a769ea6bad64"
branch_labels = None
depends_on = None


class UserRoles(str, Enum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, "before_update", cls._updated_at)


# Define tables as they were at the time of this migration
# we don't use the current models because they may have changed since this
# migration
class Organization(Base):
    __tablename__ = "organization"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    default = sa.Column(Boolean)
    projects = relationship("Project")

    search_vector = sa.Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class Project(Base):
    __tablename__ = "project"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    default = sa.Column(Boolean)
    organization_id = sa.Column(sa.Integer, sa.ForeignKey("organization.id"))

    search_vector = sa.Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class DispatchUser(Base, TimeStampMixin):
    __tablename__ = "dispatch_user"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String, unique=True)
    password = sa.Column(sa.Binary, nullable=False)
    role = sa.Column(sa.String)

    search_vector = sa.Column(TSVectorType("email", weights={"email": "A"}))


class DispatchUserOrganization(Base, TimeStampMixin):
    __tablename__ = "dispatch_user_organization"
    id = sa.Column("id", sa.Integer, primary_key=True)
    dispatch_user_id = sa.Column(sa.Integer, sa.ForeignKey("dispatch_user.id"))
    organization_id = sa.Column(sa.Integer, sa.ForeignKey("organization.id"))
    role = sa.Column(sa.String)
    dispatch_user = relationship(DispatchUser, backref="organizations")


class DispatchUserProject(Base, TimeStampMixin):
    __tablename__ = "dispatch_user_project"
    id = sa.Column("id", sa.Integer, primary_key=True)
    dispatch_user_id = sa.Column(sa.Integer, sa.ForeignKey("dispatch_user.id"))
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))
    role = sa.Column(sa.String, nullable=False, default=UserRoles.member)
    dispatch_user = relationship(DispatchUser, backref="projects")


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # Create organization table
    Organization.__table__.create(bind)

    default_org = Organization(
        name="default", default=True, description="Default dispatch organization."
    )
    session.add(default_org)
    session.flush()

    # create a project table
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("search_vector", TSVectorType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_project_search_vector",
        "project",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )

    default_project = Project(
        name="default",
        default=True,
        description="Default dispatch project.",
        organization_id=default_org.id,
    )
    session.add(default_project)
    session.flush()

    # associate users with the default organization
    op.create_table(
        "dispatch_user_organization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dispatch_user_id", sa.Integer(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dispatch_user_id"],
            ["dispatch_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # associate users with the default project
    op.create_table(
        "dispatch_user_project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dispatch_user_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dispatch_user_id"],
            ["dispatch_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # associate all users with the current default organization and project
    for u in session.query(DispatchUser).all():
        # we make all previous admins organization admins
        organization_role = None
        if u.role == "Admin":
            organization_role = "Owner"

        session.add(
            DispatchUserOrganization(
                dispatch_user_id=u.id, organization_id=default_org.id, role=organization_role
            )
        )

        # everybody is a regular project member for now
        session.add(DispatchUserProject(dispatch_user_id=u.id, project_id=default_project.id))

    # we don't need role anymore
    op.drop_column("dispatch_user", "role")
    session.flush()

    # associate resources with default project
    op.add_column("definition", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "definition", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update definition set project_id = {default_project.id}")

    op.add_column("document", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "document", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update document set project_id = {default_project.id}")

    op.add_column("incident", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "incident", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update incident set project_id = {default_project.id}")

    op.add_column("incident_cost", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "incident_cost", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update incident_cost set project_id = {default_project.id}")

    op.add_column("incident_cost_type", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "incident_cost_type", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update incident_cost_type set project_id = {default_project.id}")

    op.add_column("incident_priority", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "incident_priority", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update incident_priority set project_id = {default_project.id}")

    op.add_column("incident_type", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "incident_type", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update incident_type set project_id = {default_project.id}")

    op.add_column("individual_contact", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "individual_contact", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update individual_contact set project_id = {default_project.id}")

    op.add_column("notification", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "notification", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update notification set project_id = {default_project.id}")

    op.add_column("plugin", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "plugin", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update plugin set project_id = {default_project.id}")

    op.add_column("search_filter", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "search_filter", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update search_filter set project_id = {default_project.id}")

    op.add_column("service", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "service", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update service set project_id = {default_project.id}")

    op.add_column("tag", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "tag", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update tag set project_id = {default_project.id}")

    op.add_column("tag_type", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "tag_type", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update tag_type set project_id = {default_project.id}")

    op.add_column("team_contact", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "team_contact", "project", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.execute(f"update team_contact set project_id = {default_project.id}")

    op.add_column("term", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "term", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update term set project_id = {default_project.id}")

    op.add_column("workflow", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "workflow", "project", ["project_id"], ["id"], ondelete="CASCADE")
    op.execute(f"update workflow set project_id = {default_project.id}")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "workflow", type_="foreignkey")
    op.drop_column("workflow", "project_id")
    op.drop_constraint(None, "term", type_="foreignkey")
    op.drop_column("term", "project_id")
    op.drop_constraint(None, "team_contact", type_="foreignkey")
    op.drop_column("team_contact", "project_id")
    op.drop_constraint(None, "tag_type", type_="foreignkey")
    op.drop_column("tag_type", "project_id")
    op.drop_constraint(None, "tag", type_="foreignkey")
    op.drop_column("tag", "project_id")
    op.drop_constraint(None, "service", type_="foreignkey")
    op.drop_column("service", "project_id")
    op.drop_constraint(None, "search_filter", type_="foreignkey")
    op.drop_column("search_filter", "project_id")
    op.drop_constraint(None, "plugin", type_="foreignkey")
    op.drop_column("plugin", "project_id")
    op.drop_constraint(None, "notification", type_="foreignkey")
    op.drop_column("notification", "project_id")
    op.drop_constraint(None, "individual_contact", type_="foreignkey")
    op.drop_column("individual_contact", "project_id")
    op.drop_constraint(None, "incident_type", type_="foreignkey")
    op.drop_column("incident_type", "project_id")
    op.drop_constraint(None, "incident_priority", type_="foreignkey")
    op.drop_column("incident_priority", "project_id")
    op.drop_constraint(None, "incident_cost_type", type_="foreignkey")
    op.drop_column("incident_cost_type", "project_id")
    op.drop_constraint(None, "incident_cost", type_="foreignkey")
    op.drop_column("incident_cost", "project_id")
    op.drop_constraint(None, "incident", type_="foreignkey")
    op.drop_column("incident", "project_id")
    op.drop_constraint(None, "document", type_="foreignkey")
    op.drop_column("document", "project_id")
    op.add_column(
        "dispatch_user", sa.Column("role", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.drop_constraint(None, "definition", type_="foreignkey")
    op.drop_column("definition", "project_id")
    op.drop_table("dispatch_user_projects")
    op.drop_index("ix_project_search_vector", table_name="project")
    op.drop_table("project")
    op.drop_table("dispatch_user_organizations")
    op.drop_index("ix_organization_search_vector", table_name="organization")
    op.drop_table("organization")
    # ### end Alembic commands ###
