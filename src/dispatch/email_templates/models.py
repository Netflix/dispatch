from datetime import datetime
from pydantic import Field
from typing import Optional, List

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
    email_template_type: Optional[str] = Field(None, nullable=True)
    welcome_text: Optional[str] = Field(None, nullable=True)
    welcome_body: Optional[str] = Field(None, nullable=True)
    components: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]


class EmailTemplatesCreate(EmailTemplatesBase):
    project: Optional[ProjectRead]


class EmailTemplatesUpdate(EmailTemplatesBase):
    id: PrimaryKey = None


class EmailTemplatesRead(EmailTemplatesBase):
    id: PrimaryKey
    project: Optional[ProjectRead]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmailTemplatesPagination(Pagination):
    items: List[EmailTemplatesRead]
    total: int
