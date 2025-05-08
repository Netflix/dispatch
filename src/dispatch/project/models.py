from pydantic import EmailStr
from slugify import slugify
from pydantic import Field

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql import false
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, PrimaryKey, Pagination

from dispatch.organization.models import Organization, OrganizationRead
from dispatch.incident.priority.models import (
    IncidentPriority,
    IncidentPriorityRead,
)


class Project(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    display_name = Column(String, nullable=False, server_default="")

    description = Column(String)
    default = Column(Boolean, default=False)
    color = Column(String)

    annual_employee_cost = Column(Integer, default=50000)
    business_year_hours = Column(Integer, default=2080)

    owner_email = Column(String)
    owner_conversation = Column(String)

    organization_id = Column(Integer, ForeignKey(Organization.id))
    organization = relationship("Organization")

    dispatch_user_project = relationship(
        "DispatchUserProject",
        cascade="all, delete-orphan",
        overlaps="users"
    )

    enabled = Column(Boolean, default=True, server_default="t")
    allow_self_join = Column(Boolean, default=True, server_default="t")

    send_daily_reports = Column(Boolean)
    send_weekly_reports = Column(Boolean)

    weekly_report_notification_id = Column(Integer, nullable=True)

    select_commander_visibility = Column(Boolean, default=True, server_default="t")

    stable_priority_id = Column(Integer, nullable=True)
    stable_priority = relationship(
        IncidentPriority,
        foreign_keys=[stable_priority_id],
        primaryjoin="IncidentPriority.id == Project.stable_priority_id",
    )

    # allows for alternative names for storage folders inside incident/case
    storage_folder_one = Column(String, nullable=True)
    storage_folder_two = Column(String, nullable=True)
    # when true, storage_folder_one is used as the primary storage folder for incidents/cases
    storage_use_folder_one_as_primary = Column(Boolean, default=False, nullable=True)
    # when true, folder and incident docs will be created with the title of the incident
    storage_use_title = Column(Boolean, default=False, server_default=false())

    # allows customized instructions for reporting incidents
    report_incident_instructions = Column(String, nullable=True)
    report_incident_title_hint = Column(String, nullable=True)
    report_incident_description_hint = Column(String, nullable=True)

    snooze_extension_oncall_service_id = Column(Integer, nullable=True)
    snooze_extension_oncall_service = relationship(
        "Service",
        foreign_keys=[snooze_extension_oncall_service_id],
        primaryjoin="Service.id == Project.snooze_extension_oncall_service_id",
    )

    @hybrid_property
    def slug(self):
        return slugify(self.name)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class Service(DispatchBase):
    id: PrimaryKey
    description: str | None = Field(None, nullable=True)
    external_id: str
    is_active: bool | None = None
    name: NameStr
    type: str | None = Field(None, nullable=True)


class ProjectBase(DispatchBase):
    id: PrimaryKey | None
    name: NameStr
    display_name: str | None = Field("", nullable=False)
    owner_email: EmailStr | None = Field(None, nullable=True)
    owner_conversation: str | None = Field(None, nullable=True)
    annual_employee_cost: int | None
    business_year_hours: int | None
    description: str | None = Field(None, nullable=True)
    default: bool = False
    color: str | None = Field(None, nullable=True)
    send_daily_reports: bool | None = Field(True, nullable=True)
    send_weekly_reports: bool | None = Field(False, nullable=True)
    weekly_report_notification_id: int | None = Field(None, nullable=True)
    enabled: bool | None = Field(True, nullable=True)
    storage_folder_one: str | None = Field(None, nullable=True)
    storage_folder_two: str | None = Field(None, nullable=True)
    storage_use_folder_one_as_primary: bool | None = Field(True, nullable=True)
    storage_use_title: bool | None = Field(False, nullable=True)
    allow_self_join: bool | None = Field(True, nullable=True)
    select_commander_visibility: bool | None = Field(True, nullable=True)
    report_incident_instructions: str | None = Field(None, nullable=True)
    report_incident_title_hint: str | None = Field(None, nullable=True)
    report_incident_description_hint: str | None = Field(None, nullable=True)
    snooze_extension_oncall_service: Service | None = None


class ProjectCreate(ProjectBase):
    organization: OrganizationRead


class ProjectUpdate(ProjectBase):
    send_daily_reports: bool | None = Field(True, nullable=True)
    send_weekly_reports: bool | None = Field(False, nullable=True)
    weekly_report_notification_id: int | None = Field(None, nullable=True)
    stable_priority_id: int | None
    snooze_extension_oncall_service_id: int | None


class ProjectRead(ProjectBase):
    id: PrimaryKey | None
    stable_priority: IncidentPriorityRead | None = None


class ProjectPagination(Pagination):
    items: list[ProjectRead] = []
