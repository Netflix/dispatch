from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey, Pagination, ProjectMixin
from dispatch.project.models import ProjectRead


class EmailTemplates(TimeStampMixin, ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("email_template_type", "project_id"),)
    # Columns
    id = Column(Integer, primary_key=True)
    email_template_type = Column(String, nullable=True)
    welcome_text = Column(String, nullable=True)
    welcome_body = Column(String, nullable=True)
    components = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)


# Pydantic models
class EmailTemplatesBase(DispatchBase):
    email_template_type: str | None = None
    welcome_text: str | None = None
    welcome_body: str | None = None
    components: str | None = None
    enabled: bool | None = None


class EmailTemplatesCreate(EmailTemplatesBase):
    project: ProjectRead | None = None


class EmailTemplatesUpdate(EmailTemplatesBase):
    id: PrimaryKey = None


class EmailTemplatesRead(EmailTemplatesBase):
    id: PrimaryKey
    project: ProjectRead | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EmailTemplatesPagination(Pagination):
    items: list[EmailTemplatesRead]
    total: int
