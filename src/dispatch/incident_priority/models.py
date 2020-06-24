from typing import List, Optional
from pydantic import StrictBool

from sqlalchemy import event, Column, Integer, String, Boolean
from sqlalchemy.sql.expression import true
from sqlalchemy.orm import object_session
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class IncidentPriority(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
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


@event.listens_for(IncidentPriority.default, "set")
def _revoke_other_default(target, value, oldvalue, initiator):
    """Removes the previous default when a new one is set."""
    session = object_session(target)
    if session is None:
        return

    if value:
        previous_default = (
            session.query(IncidentPriority).filter(IncidentPriority.default == true()).one_or_none()
        )
        if previous_default:
            previous_default.default = False
            session.commit()


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: str
    description: Optional[str]
    page_commander: Optional[StrictBool]
    tactical_report_reminder: Optional[int]
    executive_report_reminder: Optional[int]
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
