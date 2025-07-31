from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean

from dispatch.models import DispatchBase
from dispatch.database.core import Base
from dispatch.models import TimeStampMixin, ProjectMixin, Pagination, PrimaryKey
from dispatch.project.models import ProjectRead


class Prompt(Base, TimeStampMixin, ProjectMixin):
    """
    SQLAlchemy model for AI prompts.

    This model stores AI prompts that can be used for various GenAI operations
    like tag recommendations, incident summaries, etc.
    """

    # Columns
    id = Column(Integer, primary_key=True)
    genai_type = Column(Integer, nullable=False)
    genai_prompt = Column(String, nullable=False)
    genai_system_message = Column(String, nullable=True)
    enabled = Column(Boolean, default=False, nullable=False)


# AI Prompt Models
class PromptBase(DispatchBase):
    genai_type: int | None = None
    genai_prompt: str | None = None
    genai_system_message: str | None = None
    enabled: bool | None = None


class PromptCreate(PromptBase):
    project: ProjectRead | None = None


class PromptUpdate(DispatchBase):
    genai_type: int | None = None
    genai_prompt: str | None = None
    genai_system_message: str | None = None
    enabled: bool | None = None


class PromptRead(PromptBase):
    id: PrimaryKey
    created_at: datetime | None = None
    updated_at: datetime | None = None
    project: ProjectRead | None = None


class PromptPagination(Pagination):
    items: list[PromptRead]
