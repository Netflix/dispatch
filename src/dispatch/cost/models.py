from datetime import datetime

from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table
from sqlalchemy_utils import JSONType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


# PCI Loss Tables
pci_disclosure_fines_judgements = Table(
    "pci_disclosure_fines_judgements",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("num_disclosed_records", Integer),
    Column("min", Integer),
    Column("max", Integer),
    Column("most_likely", Integer),
)

pci_disclosure_response_costs = Table(
    "pci_disclosure_response_costs",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("num_disclosed_records", Integer),
    Column("min", Integer),
    Column("max", Integer),
    Column("most_likely", Integer),
)

# PII Loss Tables
pii_disclosure_fines_judgements = Table(
    "pii_disclosure_fines_judgements",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("num_disclosed_records", Integer),
    Column("min", Integer),
    Column("max", Integer),
    Column("most_likely", Integer),
)

pii_disclosure_response_costs = Table(
    "pii_disclosure_response_costs",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("num_disclosed_records", Integer),
    Column("min", Integer),
    Column("max", Integer),
    Column("most_likely", Integer),
)


class Cost(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    details = Column(JSONType, nullable=True)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))


# Pydantic models...
class CostBase(DispatchBase):
    details: Optional[dict] = None


class CostCreate(CostBase):
    pass


class CostUpdate(CostBase):
    pass


class CostRead(CostBase):
    id: int
    created_at: Optional[datetime] = None


class CostPagination(CostBase):
    total: int
    items: List[CostRead] = []
