"""Refactors recommendations to use search filter expressions.

We only create tables and migrate date, we leave existing data
to be dropped in a future revision to help prevent data loss.

Revision ID: efe949b0fe55
Revises: 87400096f4cc
Create Date: 2021-04-22 11:19:07.315701

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.orm import Session

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# revision identifiers, used by Alembic.
revision = "efe949b0fe55"
down_revision = "87400096f4cc"
branch_labels = None
depends_on = None


class Project(Base):
    __tablename__ = "project"
    id = sa.Column(sa.Integer, primary_key=True)


class SearchFilter(Base):
    __tablename__ = "search_filter"
    id = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))
    name = sa.Column(sa.String)
    expression = sa.Column(sa.JSON)
    type = sa.Column(sa.String)


assoc_document_filters = sa.Table(
    "assoc_document_filters",
    Base.metadata,
    sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id", ondelete="CASCADE")),
    sa.Column(
        "search_filter_id", sa.Integer, sa.ForeignKey("search_filter.id", ondelete="CASCADE")
    ),
)

# Association tables for many to many relationships
assoc_document_incident_priorities = sa.Table(
    "document_incident_priority",
    Base.metadata,
    sa.Column("incident_priority_id", sa.Integer, sa.ForeignKey("incident_priority.id")),
    sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id")),
    sa.PrimaryKeyConstraint("incident_priority_id", "document_id"),
)

assoc_document_incident_types = sa.Table(
    "document_incident_type",
    Base.metadata,
    sa.Column("incident_type_id", sa.Integer, sa.ForeignKey("incident_type.id")),
    sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id")),
    sa.PrimaryKeyConstraint("incident_type_id", "document_id"),
)

assoc_document_terms = sa.Table(
    "document_terms",
    Base.metadata,
    sa.Column("term_id", sa.Integer, sa.ForeignKey("term.id", ondelete="CASCADE")),
    sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id", ondelete="CASCADE")),
    sa.PrimaryKeyConstraint("term_id", "document_id"),
)


class IncidentType(Base):
    __tablename__ = "incident_type"
    id = sa.Column(sa.Integer, primary_key=True)


class IncidentPriority(Base):
    __tablename__ = "incident_priority"
    id = sa.Column(sa.Integer, primary_key=True)


class Term(Base):
    __tablename__ = "term"
    id = sa.Column(sa.Integer, primary_key=True)


class Document(Base):
    __tablename__ = "document"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))

    filters = sa.orm.relationship(
        "SearchFilter", secondary=assoc_document_filters, backref="documents"
    )
    incident_priorities = sa.orm.relationship(
        "IncidentPriority", secondary=assoc_document_incident_priorities, backref="documents"
    )
    incident_types = sa.orm.relationship(
        "IncidentType", secondary=assoc_document_incident_types, backref="documents"
    )
    terms = sa.orm.relationship("Term", secondary=assoc_document_terms, backref="documents")


assoc_individual_contact_filters = sa.Table(
    "assoc_individual_contact_filters",
    Base.metadata,
    sa.Column(
        "individual_contact_id",
        sa.Integer,
        sa.ForeignKey("individual_contact.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "search_filter_id", sa.Integer, sa.ForeignKey("search_filter.id", ondelete="CASCADE")
    ),
)

assoc_individual_contact_incident_types = sa.Table(
    "assoc_individual_contact_incident_type",
    Base.metadata,
    sa.Column("incident_type_id", sa.Integer, sa.ForeignKey("incident_type.id")),
    sa.Column("individual_contact_id", sa.Integer, sa.ForeignKey("individual_contact.id")),
    sa.PrimaryKeyConstraint("incident_type_id", "individual_contact_id"),
)

assoc_individual_contact_incident_priorities = sa.Table(
    "assoc_individual_contact_incident_priority",
    Base.metadata,
    sa.Column("incident_priority_id", sa.Integer, sa.ForeignKey("incident_priority.id")),
    sa.Column("individual_contact_id", sa.Integer, sa.ForeignKey("individual_contact.id")),
    sa.PrimaryKeyConstraint("incident_priority_id", "individual_contact_id"),
)

assoc_individual_contact_terms = sa.Table(
    "assoc_individual_contact_terms",
    Base.metadata,
    sa.Column("term_id", sa.Integer, sa.ForeignKey("term.id")),
    sa.Column("individual_contact_id", sa.ForeignKey("individual_contact.id")),
    sa.PrimaryKeyConstraint("term_id", "individual_contact_id"),
)


class IndividualContact(Base):
    __tablename__ = "individual_contact"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))
    filters = sa.orm.relationship(
        "SearchFilter", secondary=assoc_individual_contact_filters, backref="individuals"
    )
    incident_types = sa.orm.relationship(
        "IncidentType", secondary=assoc_individual_contact_incident_types, backref="individuals"
    )
    incident_priorities = sa.orm.relationship(
        "IncidentPriority",
        secondary=assoc_individual_contact_incident_priorities,
        backref="individuals",
    )
    terms = sa.orm.relationship(
        "Term", secondary=assoc_individual_contact_terms, backref="individuals"
    )


assoc_team_contact_filters = sa.Table(
    "assoc_team_contact_filters",
    Base.metadata,
    sa.Column(
        "team_contact_id",
        sa.Integer,
        sa.ForeignKey("team_contact.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "search_filter_id", sa.Integer, sa.ForeignKey("search_filter.id", ondelete="CASCADE")
    ),
)

assoc_team_contact_incident_priorities = sa.Table(
    "team_contact_incident_priority",
    Base.metadata,
    sa.Column("incident_priority_id", sa.Integer, sa.ForeignKey("incident_priority.id")),
    sa.Column("team_contact_id", sa.Integer, sa.ForeignKey("team_contact.id")),
    sa.PrimaryKeyConstraint("incident_priority_id", "team_contact_id"),
)

assoc_team_contact_incident_types = sa.Table(
    "team_contact_incident_type",
    Base.metadata,
    sa.Column("incident_type_id", sa.Integer, sa.ForeignKey("incident_type.id")),
    sa.Column("team_contact_id", sa.Integer, sa.ForeignKey("team_contact.id")),
    sa.PrimaryKeyConstraint("incident_type_id", "team_contact_id"),
)


assoc_team_contact_terms = sa.Table(
    "team_contact_terms",
    Base.metadata,
    sa.Column("term_id", sa.Integer, sa.ForeignKey("term.id")),
    sa.Column("team_contact_id", sa.ForeignKey("team_contact.id")),
    sa.PrimaryKeyConstraint("term_id", "team_contact_id"),
)


class TeamContact(Base):
    __tablename__ = "team_contact"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))
    filters = sa.orm.relationship(
        "SearchFilter", secondary=assoc_team_contact_filters, backref="teams"
    )
    incident_priorities = sa.orm.relationship(
        "IncidentPriority", secondary=assoc_team_contact_incident_priorities, backref="teams"
    )
    incident_types = sa.orm.relationship(
        "IncidentType", secondary=assoc_team_contact_incident_types, backref="teams"
    )
    terms = sa.orm.relationship("Term", secondary=assoc_team_contact_terms, backref="teams")


# Association tables for many to many relationships
assoc_service_incident_priorities = sa.Table(
    "service_incident_priority",
    Base.metadata,
    sa.Column("incident_priority_id", sa.Integer, sa.ForeignKey("incident_priority.id")),
    sa.Column("service_id", sa.Integer, sa.ForeignKey("service.id")),
    sa.PrimaryKeyConstraint("incident_priority_id", "service_id"),
)

assoc_service_incident_types = sa.Table(
    "service_incident_type",
    Base.metadata,
    sa.Column("incident_type_id", sa.Integer, sa.ForeignKey("incident_type.id")),
    sa.Column("service_id", sa.Integer, sa.ForeignKey("service.id")),
    sa.PrimaryKeyConstraint("incident_type_id", "service_id"),
)

assoc_service_terms = sa.Table(
    "service_terms",
    Base.metadata,
    sa.Column("term_id", sa.Integer, sa.ForeignKey("term.id")),
    sa.Column("service_id", sa.Integer, sa.ForeignKey("service.id")),
    sa.PrimaryKeyConstraint("term_id", "service_id"),
)


assoc_service_filters = sa.Table(
    "assoc_service_filters",
    Base.metadata,
    sa.Column("service_id", sa.Integer, sa.ForeignKey("service.id", ondelete="CASCADE")),
    sa.Column(
        "search_filter_id", sa.Integer, sa.ForeignKey("search_filter.id", ondelete="CASCADE")
    ),
)


class Service(Base):
    __tablename__ = "service"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.id"))
    filters = sa.orm.relationship(
        "SearchFilter", secondary=assoc_service_filters, backref="services"
    )
    incident_priorities = sa.orm.relationship(
        "IncidentPriority", secondary=assoc_service_incident_priorities, backref="services"
    )
    incident_types = sa.orm.relationship(
        "IncidentType", secondary=assoc_service_incident_types, backref="services"
    )
    terms = sa.orm.relationship("Term", secondary=assoc_service_terms, backref="services")


# setup models needed for migration
def engagement_models_to_search_filter(model):
    expression = {"and": []}
    term_filter = {"or": []}
    for term in model.terms:
        term_filter["or"].append({"model": "Term", "field": "id", "op": "==", "value": term.id})

    if term_filter["or"]:
        expression["and"].append(term_filter)

    incident_type_filter = {"or": []}
    for incident_type in model.incident_types:
        incident_type_filter["or"].append(
            {"model": "IncidentType", "field": "id", "op": "==", "value": incident_type.id}
        )

    if incident_type_filter["or"]:
        expression["and"].append(incident_type_filter)

    incident_priority_filter = {"or": []}
    for incident_priority in model.incident_priorities:
        incident_priority_filter["or"].append(
            {
                "model": "IncidentPriority",
                "field": "id",
                "op": "==",
                "value": incident_priority.id,
            }
        )

    if incident_priority_filter["or"]:
        expression["and"].append(incident_priority_filter)

    return SearchFilter(
        name=f"Migrated - {model.name}",
        project_id=model.project_id,
        expression=expression,
        type="incident",
    )


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)

    op.create_table(
        "recommendation_match",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_state", sqlalchemy_utils.types.json.JSONType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recommendation_id"],
            ["recommendation.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assoc_document_filters",
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("search_filter_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["document.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["search_filter_id"], ["search_filter.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("document_id", "search_filter_id"),
    )
    op.create_table(
        "assoc_service_filters",
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("search_filter_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["search_filter_id"], ["search_filter.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["service.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("service_id", "search_filter_id"),
    )
    op.create_table(
        "assoc_team_contact_filters",
        sa.Column("team_contact_id", sa.Integer(), nullable=False),
        sa.Column("search_filter_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["search_filter_id"], ["search_filter.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_contact_id"], ["team_contact.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("team_contact_id", "search_filter_id"),
    )
    op.create_table(
        "assoc_individual_contact_filters",
        sa.Column("individual_contact_id", sa.Integer(), nullable=False),
        sa.Column("search_filter_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["individual_contact_id"], ["individual_contact.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["search_filter_id"], ["search_filter.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("individual_contact_id", "search_filter_id"),
    )

    op.add_column("recommendation", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("recommendation", sa.Column("incident_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "recommendation", "incident", ["incident_id"], ["id"])

    # migrate the data

    # documents
    for d in session.query(Document).all():
        if any([d.incident_priorities, d.incident_types, d.terms]):
            filters = engagement_models_to_search_filter(d)
            d.filters = [filters]
            session.add(d)

    # individuals
    for i in session.query(IndividualContact).all():
        if any([i.incident_priorities, i.incident_types, i.terms]):
            filters = engagement_models_to_search_filter(i)
            i.filters = [filters]
            session.add(i)

    # teams
    for t in session.query(TeamContact).all():
        if any([t.incident_priorities, t.incident_types, t.terms]):
            filters = engagement_models_to_search_filter(t)
            t.filters = [filters]
            session.add(t)

    # services
    for s in session.query(Service).all():
        if any([s.incident_priorities, s.incident_types, s.terms]):
            filters = engagement_models_to_search_filter(s)
            s.filters = [filters]
            session.add(s)

    session.flush()

    # ### end Alembic commands ###


def downgrade():
    pass
