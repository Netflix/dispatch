from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.incident_cost_type.models import (
    IncidentCostTypeCreate,
    IncidentCostTypeUpdate,
    IncidentCostTypeRead,
)
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class IncidentCost(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)

    # relationships
    incident_cost_type = relationship("IncidentCostType", backref="incident_cost")
    incident_cost_type_id = Column(Integer, ForeignKey("incident_cost_type.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))


# Pydantic Models
class IncidentCostBase(DispatchBase):
    amount: float


class IncidentCostCreate(IncidentCostBase):
    incident_cost_type: IncidentCostTypeCreate


class IncidentCostUpdate(IncidentCostBase):
    id: int
    incident_cost_type: IncidentCostTypeUpdate


class IncidentCostRead(IncidentCostBase):
    id: int
    incident_cost_type: IncidentCostTypeRead
