from datetime import datetime
from pydantic import Field

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey, Pagination, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.incident.models import IncidentReadMinimal
from dispatch.forms.type.models import FormsTypeRead
from .enums import FormStatus, FormAttorneyStatus


class Forms(TimeStampMixin, ProjectMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    form_data = Column(String, nullable=True)
    status = Column(String, default=FormStatus.new, nullable=True)
    attorney_status = Column(String, default=FormAttorneyStatus.not_reviewed, nullable=True)
    attorney_questions = Column(String, nullable=True)
    attorney_analysis = Column(String, nullable=True)

    # Relationships
    creator_id = Column(Integer, ForeignKey("individual_contact.id"))
    creator = relationship("IndividualContact")

    incident_id = Column(Integer, ForeignKey("incident.id"))
    incident = relationship("Incident")

    form_type_id = Column(Integer, ForeignKey("forms_type.id"))
    form_type = relationship("FormsType")


# Pydantic models
class FormsBase(DispatchBase):
    form_type: FormsTypeRead | None
    creator: IndividualContactReadMinimal | None
    form_data: str | None = Field(None, nullable=True)
    status: str | None = Field(None, nullable=True)
    attorney_status: str | None = Field(None, nullable=True)
    project: ProjectRead | None
    incident: IncidentReadMinimal | None
    attorney_questions: str | None = Field(None, nullable=True)
    attorney_analysis: str | None = Field(None, nullable=True)


class FormsCreate(FormsBase):
    pass


class FormsUpdate(FormsBase):
    id: PrimaryKey = None


class FormsRead(FormsBase):
    id: PrimaryKey
    project: ProjectRead | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FormsPagination(Pagination):
    items: list[FormsRead]
    total: int
