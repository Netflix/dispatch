from typing import List, Optional
from dispatch.models import PrimaryKey

from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.ext.associationproxy import association_proxy

from dispatch.database.core import Base
from dispatch.incident_cost_type.models import (
    IncidentCostTypeRead,
)
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
from dispatch.project.models import ProjectRead


# SQLAlchemy Model
class IncidentCost(Base, TimeStampMixin, ProjectMixin):
    # columns
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=True)

    # relationships
    incident_cost_type = relationship("IncidentCostType", backref="incident_cost")
    incident_cost_type_id = Column(Integer, ForeignKey("incident_cost_type.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))
    search_vector = association_proxy("incident_cost_type", "search_vector")


# Pydantic Models
class IncidentCostBase(DispatchBase):
    amount: float = 0


class IncidentCostCreate(IncidentCostBase):
    incident_cost_type: IncidentCostTypeRead
    project: ProjectRead


class IncidentCostUpdate(IncidentCostBase):
    id: Optional[PrimaryKey] = None
    incident_cost_type: IncidentCostTypeRead


class IncidentCostRead(IncidentCostBase):
    id: PrimaryKey
    incident_cost_type: IncidentCostTypeRead


class IncidentCostNested(IncidentCostBase):
    id: PrimaryKey


class IncidentCostPagination(DispatchBase):
    total: int
    items: List[IncidentCostRead] = []
