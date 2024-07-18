"""Creates alternative storage attributes in project

Revision ID: a812a4cf61e1
Revises: 15a8d3228123
Create Date: 2024-04-12 14:48:05.481102

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a812a4cf61e1"
down_revision = "15a8d3228123"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("project", sa.Column("storage_folder_one", sa.String(), nullable=True))
    op.add_column("project", sa.Column("storage_folder_two", sa.String(), nullable=True))
    op.add_column(
        "project", sa.Column("storage_use_folder_one_as_primary", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "project",
        sa.Column(
            "storage_use_title", sa.Boolean(), server_default=sa.text("false"), nullable=True
        ),
    )
    op.add_column(
        "tag_type",
        sa.Column(
            "use_for_project_folder",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("project", "storage_use_folder_one_as_primary")
    op.drop_column("project", "storage_folder_two")
    op.drop_column("project", "storage_folder_one")
    op.drop_column("project", "storage_use_title")
    op.drop_column("tag_type", "use_for_project_folder")
    # ### end Alembic commands ###