from datetime import datetime

from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class IncidentUpdate(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    overview = Column(String)
    current_status = Column(String)
    next_steps = Column(String)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))
    participant_id = Column(Integer, ForeignKey("participant.id"))
    document = relationship("Document", uselist=False, backref="incident_update")


# Pydantic models...
class IncidentUpdateBase(DispatchBase):
    overview: str
    current_status: str
    next_steps: str


class IncidentUpdateCreate(IncidentUpdateBase):
    pass


class IncidentUpdateUpdate(IncidentUpdateBase):
    pass


class IncidentUpdateRead(IncidentUpdateBase):
    id: int
    created_at: Optional[datetime] = None


class IncidentUpdatePagination(IncidentUpdateBase):
    total: int
    items: List[IncidentUpdateRead] = []
