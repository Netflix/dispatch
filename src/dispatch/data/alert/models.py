from pydantic import Field

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey, Pagination


class Alert(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    orginator = Column(String)
    external_link = Column(String)
    source_id = Column(Integer, ForeignKey("source.id"))
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class AlertBase(DispatchBase):
    name: str | None = Field(None, nullable=False)
    description: str | None = None
    originator: str | None = None
    external_link: str | None = None


class AlertCreate(AlertBase):
    id: PrimaryKey | None = None


class AlertUpdate(AlertBase):
    id: PrimaryKey | None


class AlertRead(AlertBase):
    id: PrimaryKey


class AlertPagination(Pagination):
    items: list[AlertRead]
