from datetime import datetime


from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType, TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, Pagination

from .enums import ReportTypes


class Report(Base):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    details = Column(JSONType, nullable=True)
    details_raw = Column(String, nullable=True)
    type = Column(String, nullable=False, server_default=ReportTypes.tactical_report)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE", use_alter=True))
    participant_id = Column(Integer, ForeignKey("participant.id"))
    document = relationship("Document", uselist=False, backref="report")

    # full text search capabilities
    search_vector = Column(TSVectorType("details_raw"))

    @staticmethod
    def _details_raw(mapper, connection, target):
        target.details_raw = " ".join(target.details.values())

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._details_raw)


# Pydantic models...
class ReportBase(DispatchBase):
    details: dict | None = None
    type: ReportTypes


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    created_at: datetime | None = None


class ReportPagination(Pagination):
    items: list[ReportRead] = []


class TacticalReportCreate(DispatchBase):
    conditions: str
    actions: str
    needs: str


class ExecutiveReportCreate(DispatchBase):
    current_status: str
    overview: str
    next_steps: str
