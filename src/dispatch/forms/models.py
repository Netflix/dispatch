from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey, Pagination, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.incident.models import IncidentReadBasic
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
    attorney_form_data = Column(String, nullable=True)

    # Relationships
    creator_id = Column(Integer, ForeignKey("individual_contact.id"))
    creator = relationship("IndividualContact")

    incident_id = Column(Integer, ForeignKey("incident.id"))
    incident = relationship("Incident")

    form_type_id = Column(Integer, ForeignKey("forms_type.id"))
    form_type = relationship("FormsType")

    score = Column(Integer, nullable=True)


# Pydantic models
class FormsBase(DispatchBase):
    form_type: FormsTypeRead | None
    creator: IndividualContactReadMinimal | None
    form_data: str | None = None
    attorney_form_data: str | None = None
    status: str | None = None
    attorney_status: str | None = None
    project: ProjectRead | None
    incident: IncidentReadBasic | None
    attorney_questions: str | None = None
    attorney_analysis: str | None = None
    score: int | None


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
