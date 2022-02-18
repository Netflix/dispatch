from typing import Optional, List
from pydantic import Field

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey


class Alert(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    orginator = Column(String)
    external_link = Column(String)
    source_id = Column(Integer, ForeignKey("source.id"))
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class AlertBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=False)
    description: Optional[str] = Field(None, nullable=True)
    originator: Optional[str] = Field(None, nullable=True)
    external_link: Optional[str] = Field(None, nullable=True)


class AlertCreate(AlertBase):
    id: Optional[PrimaryKey]


class AlertUpdate(AlertBase):
    id: Optional[PrimaryKey]


class AlertRead(AlertBase):
    id: PrimaryKey


class AlertPagination(DispatchBase):
    items: List[AlertRead]
    total: int
