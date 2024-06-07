from datetime import datetime
from pydantic import Field
from typing import List, Optional

from sqlalchemy import Boolean, Column, Integer, ForeignKey, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.models import (
    DispatchBase,
    NameStr,
    Pagination,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
)
from dispatch.project.models import ProjectRead
from dispatch.service.models import ServiceRead


class FormsType(ProjectMixin, TimeStampMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    form_schema = Column(String, nullable=True)
    attorney_form_schema = Column(String, nullable=True)
    scoring_schema = Column(String, nullable=True)

    # Relationships
    creator_id = Column(Integer, ForeignKey("individual_contact.id"))
    creator = relationship("IndividualContact")

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service")


# Pydantic models
class FormsTypeBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    form_schema: Optional[str] = Field(None, nullable=True)
    attorney_form_schema: Optional[str] = Field(None, nullable=True)
    scoring_schema: Optional[str] = Field(None, nullable=True)
    creator: Optional[IndividualContactReadMinimal]
    project: Optional[ProjectRead]
    service: Optional[ServiceRead]


class FormsTypeCreate(FormsTypeBase):
    pass


class FormsTypeUpdate(FormsTypeBase):
    id: PrimaryKey = None


class FormsTypeRead(FormsTypeBase):
    id: PrimaryKey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FormsTypePagination(Pagination):
    items: List[FormsTypeRead] = []
