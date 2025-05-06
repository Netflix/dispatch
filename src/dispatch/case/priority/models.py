"""Models and schemas for the Dispatch case priority system."""
from pydantic import Field
from pydantic_extra_types.color import Color

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey, Pagination
from dispatch.project.models import ProjectRead


class CasePriority(Base, ProjectMixin):
    """SQLAlchemy model for a case priority, representing the priority level of a case."""
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    page_assignee = Column(Boolean, default=False)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)

    # This column is used to control how priorities should be displayed
    # Lower numbers will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(TSVectorType("name", "description"))


default_listener_doc = """Ensure only one default priority per project by listening to the 'default' field."""

listen(CasePriority.default, "set", ensure_unique_default_per_project)


# Pydantic models
class CasePriorityBase(DispatchBase):
    """Base Pydantic model for case priority data."""
    color: Color | None = Field(None, nullable=True)
    default: bool | None
    page_assignee: bool | None
    description: str | None = Field(None, nullable=True)
    enabled: bool | None
    name: NameStr
    project: ProjectRead | None
    view_order: int | None


class CasePriorityCreate(CasePriorityBase):
    """Pydantic model for creating a new case priority."""
    pass


class CasePriorityUpdate(CasePriorityBase):
    """Pydantic model for updating a case priority."""
    pass


class CasePriorityRead(CasePriorityBase):
    """Pydantic model for reading case priority data."""
    id: PrimaryKey | None


class CasePriorityPagination(Pagination):
    """Pydantic model for paginated case priority results."""
    items: list[CasePriorityRead] = []
