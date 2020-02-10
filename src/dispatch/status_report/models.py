from datetime import datetime

from typing import List, Optional

from dispatch.database import Base
from dispatch.models import DispatchBase

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey


class StatusReport(Base):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conditions = Column(String)
    actions = Column(String)
    needs = Column(String)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    participant_id = Column(Integer, ForeignKey("participant.id"))


# Pydantic models...
class StatusReportBase(DispatchBase):
    conditions: str
    actions: str
    needs: str


class StatusReportCreate(StatusReportBase):
    pass


class StatusReportUpdate(StatusReportBase):
    pass


class StatusReportRead(StatusReportBase):
    id: int
    created_at: Optional[datetime] = None


class StatusReportPagination(StatusReportBase):
    total: int
    items: List[StatusReportRead] = []
