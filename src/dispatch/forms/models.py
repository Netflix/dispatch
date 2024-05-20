from datetime import datetime
from pydantic import Field
from typing import Optional, List

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
    attorney_form_data = Column(String, nullable=True)

    # Relationships
    creator_id = Column(Integer, ForeignKey("individual_contact.id"))
    creator = relationship("IndividualContact")

    incident_id = Column(Integer, ForeignKey("incident.id"))
    incident = relationship("Incident")

    form_type_id = Column(Integer, ForeignKey("forms_type.id"))
    form_type = relationship("FormsType")


# Pydantic models
class FormsBase(DispatchBase):
    form_type: Optional[FormsTypeRead]
    creator: Optional[IndividualContactReadMinimal]
    form_data: Optional[str] = Field(None, nullable=True)
    attorney_form_data: Optional[str] = Field(None, nullable=True)
    status: Optional[str] = Field(None, nullable=True)
    attorney_status: Optional[str] = Field(None, nullable=True)
    project: Optional[ProjectRead]
    incident: Optional[IncidentReadMinimal]
    attorney_questions: Optional[str] = Field(None, nullable=True)
    attorney_analysis: Optional[str] = Field(None, nullable=True)


class FormsCreate(FormsBase):
    pass


class FormsUpdate(FormsBase):
    id: PrimaryKey = None


class FormsRead(FormsBase):
    id: PrimaryKey
    project: Optional[ProjectRead]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FormsPagination(Pagination):
    items: List[FormsRead]
    total: int
