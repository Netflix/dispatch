from typing import List, Optional
from pydantic import StrictBool

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, ProjectMixin
from dispatch.project.models import ProjectRead


class IncidentPriority(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    page_commander = Column(Boolean, default=False)

    # number of hours after which reports should be sent.
    tactical_report_reminder = Column(Integer, default=24, server_default="24")
    executive_report_reminder = Column(Integer, default=24, server_default="24")
    default = Column(Boolean, default=False)

    # This column is used to control how priorities should be displayed.
    # Lower orders will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(TSVectorType("name", "description"))


listen(IncidentPriority.default, "set", ensure_unique_default_per_project)


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: str
    description: Optional[str]
    page_commander: Optional[StrictBool]
    tactical_report_reminder: Optional[int]
    executive_report_reminder: Optional[int]
    project: Optional[ProjectRead]
    default: Optional[bool]
    view_order: Optional[int]


class IncidentPriorityCreate(IncidentPriorityBase):
    pass


class IncidentPriorityUpdate(IncidentPriorityBase):
    pass


class IncidentPriorityRead(IncidentPriorityBase):
    id: int


class IncidentPriorityPagination(DispatchBase):
    total: int
    items: List[IncidentPriorityRead] = []
