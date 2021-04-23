from typing import List, Optional
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
)
from dispatch.incident.models import IncidentRead


class RecommendationMatch(Base):
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation.id"))
    correct = Column(Boolean)
    resource_type = Column(String)
    resource_state = Column(JSONType)


class Recommendation(Base):
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("RecommendationMatch")


# Pydantic models...
class RecommendationMatchBase(DispatchBase):
    correct = bool
    resource_type = str
    resource_state = dict


class RecommendationBase(DispatchBase):
    matches = Optional[List[RecommendationMatchBase]]


class RouteBase(DispatchBase):
    incident: IncidentRead


class RouteRequest(RouteBase):
    pass


class RouteResponse(RouteBase):
    recommendation: RecommendationBase
