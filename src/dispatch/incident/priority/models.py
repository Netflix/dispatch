"""Models for incident priority resources in the Dispatch application."""
from pydantic import StrictBool
from pydantic_extra_types.color import Color

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey, Pagination


class IncidentPriority(Base, ProjectMixin):
    """SQLAlchemy model for incident priority resources."""
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    page_commander = Column(Boolean, default=False)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)
    disable_delayed_message_warning = Column(Boolean, default=False)

    # number of hours after which reports should be sent.
    tactical_report_reminder = Column(Integer, default=24, server_default="24")
    executive_report_reminder = Column(Integer, default=24, server_default="24")

    # This column is used to control how priorities should be displayed.
    # Lower orders will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(TSVectorType("name", "description"))


listen(IncidentPriority.default, "set", ensure_unique_default_per_project)


class ProjectRead(DispatchBase):
    """Pydantic model for reading a project resource."""
    id: PrimaryKey | None
    name: NameStr
    display_name: str | None


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    """Base Pydantic model for incident priority resources."""
    name: NameStr
    description: str | None = None
    page_commander: StrictBool | None = None
    tactical_report_reminder: int | None = None
    executive_report_reminder: int | None = None
    project: ProjectRead | None = None
    default: bool | None = None
    enabled: bool | None = None
    view_order: int | None = None
    color: Color | None = None
    disable_delayed_message_warning: bool | None = None


class IncidentPriorityCreate(IncidentPriorityBase):
    """Pydantic model for creating an incident priority resource."""
    pass


class IncidentPriorityUpdate(IncidentPriorityBase):
    """Pydantic model for updating an incident priority resource."""
    pass


class IncidentPriorityRead(IncidentPriorityBase):
    """Pydantic model for reading an incident priority resource."""
    id: PrimaryKey


class IncidentPriorityReadMinimal(DispatchBase):
    """Pydantic model for reading a minimal incident priority resource."""
    id: PrimaryKey
    name: NameStr
    description: str | None = None
    page_commander: StrictBool | None = None
    tactical_report_reminder: int | None = None
    executive_report_reminder: int | None = None
    default: bool | None = None
    enabled: bool | None = None
    view_order: int | None = None
    color: Color | None = None


class IncidentPriorityPagination(Pagination):
    """Pydantic model for paginated incident priority results."""
    items: list[IncidentPriorityRead] = []
