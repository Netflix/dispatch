"""empty message

Revision ID: da444de005a6
Revises: 2f18776252bb
Create Date: 2025-03-04 10:06:46.787201

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da444de005a6"
down_revision = "2f18776252bb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("case_cost_type", sa.Column("model_type", sa.String(), nullable=True))

    # Update 'model_type' to 'New' where 'default' is true
    op.execute(
        """
        UPDATE case_cost_type
        SET model_type = 'New'
        WHERE "default" = true
        """
    )

    op.drop_column("case_cost_type", "default")
    # ### end Alembic commands ###


def downgrade():
    op.add_column(
        "case_cost_type",
        sa.Column("default", sa.Boolean(), server_default=False),
    )
    op.execute(
        """
        UPDATE case_cost_type
        SET "default" = true
        WHERE model_type = 'New'
        """
    )
    op.drop_column("case_cost_type", "model_type")
    # ### end Alembic commands ###
