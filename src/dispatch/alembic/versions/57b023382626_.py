"""Data migration, renaming common document resource types.

Revision ID: 57b023382626
Revises: 50972429e3f0
Create Date: 2020-06-24 13:14:43.792617

"""
from alembic import op
import sqlalchemy as sa
from dispatch.document.models import Document


# revision identifiers, used by Alembic.
revision = "57b023382626"
down_revision = "50972429e3f0"
branch_labels = None
depends_on = None

SHEET = ("google-docs-investigation-sheet", "dispatch-incident-sheet")
INVESTIGATION = ("google-docs-investigation-document", "dispatch-incident-document")
REVIEW = ("google-docs-incident-review-document", "dispatch-incident-review-document")
REPORT = ("google-docs-executive-report-document", "dispatch-executive-report-document")


def upgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    for i in [SHEET, INVESTIGATION, REVIEW, REPORT]:
        objs = session.query(Document).filter(Document.resource_type == i[0])
        for o in objs:
            o.resource_type = i[1]
    session.commit()


def downgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    for i in [SHEET, INVESTIGATION, REVIEW, REPORT]:
        objs = session.query(Document).filter(Document.resource_type == i[1])
        for o in objs:
            o.resource_type = i[0]
    session.commit()
