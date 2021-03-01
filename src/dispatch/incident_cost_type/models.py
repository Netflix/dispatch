from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, event
from sqlalchemy.orm import object_session
from sqlalchemy.sql.expression import true
from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class IncidentCostType(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=False)
    details = Column(JSONType, nullable=True)
    default = Column(Boolean, default=False)

    # full text search capabilities
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


@event.listens_for(IncidentCostType.default, "set")
def _revoke_other_default(target, value, oldvalue, initiator):
    """Removes the previous default when a new one is set."""
    session = object_session(target)
    if session is None:
        return

    if value:
        previous_default = (
            session.query(IncidentCostType).filter(IncidentCostType.default == true()).one_or_none()
        )

        if previous_default:
            previous_default.default = False
            session.commit()


# Pydantic Models
class IncidentCostTypeBase(DispatchBase):
    name: str
    description: Optional[str]
    details: Optional[dict]


class IncidentCostTypeCreate(IncidentCostTypeBase):
    default: Optional[bool] = False


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    default: Optional[bool] = False


class IncidentCostTypeRead(IncidentCostTypeBase):
    default: Optional[bool] = False


class IncidentCostTypeNested(IncidentCostTypeBase):
    id: int


class IncidentCostTypePagination(DispatchBase):
    total: int
    items: List[IncidentCostTypeRead] = []
