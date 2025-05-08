from datetime import datetime
from pydantic import Field

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
    description: str | None = Field(None, nullable=True)
    enabled: bool | None
    form_schema: str | None = Field(None, nullable=True)
    attorney_form_schema: str | None = Field(None, nullable=True)
    scoring_schema: str | None = Field(None, nullable=True)
    creator: IndividualContactReadMinimal | None
    project: ProjectRead | None
    service: ServiceRead | None


class FormsTypeCreate(FormsTypeBase):
    pass


class FormsTypeUpdate(FormsTypeBase):
    id: PrimaryKey = None


class FormsTypeRead(FormsTypeBase):
    id: PrimaryKey
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FormsTypePagination(Pagination):
    items: list[FormsTypeRead] = []
