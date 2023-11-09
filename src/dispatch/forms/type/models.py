from datetime import datetime
from pydantic import Field
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.models import DispatchBase, NameStr, Pagination, PrimaryKey, ProjectMixin
from dispatch.project.models import ProjectRead


class FormsType(ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    form_schema = Column(String, nullable=True)

    # Relationships
    creator_id = Column(Integer, ForeignKey("individual_contact.id"))
    creator = relationship("IndividualContact")

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class FormsTypeBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    form_schema: Optional[str] = Field(None, nullable=True)
    creator: Optional[IndividualContactReadMinimal]
    project: Optional[ProjectRead]


class FormsTypeCreate(FormsTypeBase):
    pass


class FormsTypeUpdate(FormsTypeBase):
    id: PrimaryKey = None


class FormsTypeRead(FormsTypeBase):
    id: PrimaryKey


class FormsTypePagination(Pagination):
    items: List[FormsTypeRead] = []
