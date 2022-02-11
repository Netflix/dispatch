from typing import Optional, List
from pydantic import Field

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey


class Query(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    text = Column(String)
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class QueryBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=False)
    description: Optional[str] = Field(None, nullable=True)
    text: Optional[str] = Field(None, nullable=True)


class QueryCreate(QueryBase):
    pass


class QueryUpdate(QueryBase):
    id: Optional[PrimaryKey]


class QueryRead(QueryBase):
    id: PrimaryKey


class QueryPagination(DispatchBase):
    items: List[QueryRead]
    total: int
