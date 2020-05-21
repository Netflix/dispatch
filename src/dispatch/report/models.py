from datetime import datetime

from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from dispatch.database import Base
from dispatch.models import DispatchBase

from .enums import ReportTypes


class Report(Base):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conditions = Column(String)
    actions = Column(String)
    needs = Column(String)
    overview = Column(String)
    current_status = Column(String)
    next_steps = Column(String)
    report_type = Column(String, nullable=False, server_default=ReportTypes.status_report)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))
    participant_id = Column(Integer, ForeignKey("participant.id"))
    document = relationship("Document", uselist=False, backref="report")


# Pydantic models...
class ReportBase(DispatchBase):
    conditions: Optional[str] = None
    actions: Optional[str] = None
    needs: Optional[str] = None
    overview: Optional[str] = None
    current_status: Optional[str] = None
    next_steps: Optional[str] = None
    report_type: ReportTypes


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    created_at: Optional[datetime] = None


class ReportPagination(ReportBase):
    total: int
    items: List[ReportRead] = []
