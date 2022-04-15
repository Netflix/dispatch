from typing import List, Optional
from pydantic import StrictBool, Field
from pydantic.color import Color

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class IncidentPriority(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    page_commander = Column(Boolean, default=False)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)

    # number of hours after which reports should be sent.
    tactical_report_reminder = Column(Integer, default=24, server_default="24")
    executive_report_reminder = Column(Integer, default=24, server_default="24")

    # This column is used to control how priorities should be displayed.
    # Lower orders will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(TSVectorType("name", "description"))


listen(IncidentPriority.default, "set", ensure_unique_default_per_project)


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    page_commander: Optional[StrictBool]
    tactical_report_reminder: Optional[int]
    executive_report_reminder: Optional[int]
    project: Optional[ProjectRead]
    default: Optional[bool]
    enabled: Optional[bool]
    view_order: Optional[int]
    color: Optional[Color] = Field(None, nullable=True)


class IncidentPriorityCreate(IncidentPriorityBase):
    pass


class IncidentPriorityUpdate(IncidentPriorityBase):
    pass


class IncidentPriorityRead(IncidentPriorityBase):
    id: PrimaryKey


class IncidentPriorityPagination(DispatchBase):
    total: int
    items: List[IncidentPriorityRead] = []
