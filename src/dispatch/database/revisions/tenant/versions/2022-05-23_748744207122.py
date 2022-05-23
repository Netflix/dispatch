"""Fixes missing resource foreign keys in the incident table

Revision ID: 748744207122
Revises: e40aefe7fc4d
Create Date: 2022-05-23 10:18:10.080916

"""
from enum import Enum

from alembic import op

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session


# revision identifiers, used by Alembic.
revision = "748744207122"
down_revision = "e40aefe7fc4d"
branch_labels = None
depends_on = None

Base = declarative_base()


class DispatchEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class DocumentResourceTypes(DispatchEnum):
    incident = "dispatch-incident-document"
    review = "dispatch-incident-review-document"


class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    resource_type = Column(String)


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    resource_type = Column(String)


class Incident(Base):
    __tablename__ = "incident"
    id = Column(Integer, primary_key=True)

    documents = relationship("Document", foreign_keys=[Document.incident_id])
    groups = relationship("Group", foreign_keys=[Group.incident_id])

    incident_document_id = Column(Integer, ForeignKey("document.id"))
    incident_review_document_id = Column(Integer, ForeignKey("document.id"))
    tactical_group_id = Column(Integer, ForeignKey("group.id"))
    notifications_group_id = Column(Integer, ForeignKey("group.id"))


def get_current_document(documents, resource_type):
    for d in documents:
        if d.resource_type == resource_type:
            return d


def get_current_group(groups, resource_type):
    for g in groups:
        if g.resource_type:
            if g.resource_type.endswith(resource_type):
                return g


def upgrade():
    print("Fixing resource foreign keys in incident table...")

    bind = op.get_bind()
    session = Session(bind=bind)

    incidents = session.query(Incident).all()

    for incident in incidents:
        # we set the incident document and post-incident review document foreign keys
        incident_document = get_current_document(incident.documents, DocumentResourceTypes.incident)
        if incident_document:
            incident.incident_document_id = incident_document.id

        incident_review_document = get_current_document(
            incident.documents, DocumentResourceTypes.review
        )
        if incident_review_document:
            incident.incident_review_document_id = incident_review_document.id

        # we set the tactical and notifications foreign keys
        tactical_group = get_current_group(incident.groups, "tactical-group")
        if tactical_group:
            incident.tactical_group_id = tactical_group.id

        notifications_group = get_current_group(incident.groups, "notification-group")
        if not notifications_group:
            # we check for the current resource type name
            notifications_group = get_current_group(incident.groups, "notifications-group")

        if notifications_group:
            incident.notifications_group_id = notifications_group.id

    session.commit()

    print("Incident resource foreign keys fixed.")
    # ### end Alembic commands ###


def downgrade():
    pass
