from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing import List, Optional

from dispatch.database.core import Base
from dispatch.case_cost_type.models import CaseCostTypeRead
from dispatch.models import DispatchBase, Pagination, PrimaryKey, ProjectMixin, TimeStampMixin
from dispatch.project.models import ProjectRead


# SQLAlchemy Model
class CaseCost(Base, TimeStampMixin, ProjectMixin):
    # columns
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=True)

    # relationships
    case_cost_type = relationship("CaseCostType", backref="case_cost")
    case_cost_type_id = Column(Integer, ForeignKey("case_cost_type.id"))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    search_vector = association_proxy("case_cost_type", "search_vector")


# Pydantic Models
class CaseCostBase(DispatchBase):
    amount: float = 0


class CaseCostCreate(CaseCostBase):
    case_cost_type: CaseCostTypeRead
    project: ProjectRead


class CaseCostUpdate(CaseCostBase):
    id: Optional[PrimaryKey] = None
    case_cost_type: CaseCostTypeRead


class CaseCostRead(CaseCostBase):
    id: PrimaryKey
    case_cost_type: CaseCostTypeRead


class CaseCostPagination(Pagination):
    items: List[CaseCostRead] = []
