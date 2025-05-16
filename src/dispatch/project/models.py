from pydantic import ConfigDict, EmailStr, Field
from slugify import slugify
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.priority.models import (
    IncidentPriority,
    IncidentPriorityRead,
)
from dispatch.models import DispatchBase, NameStr, Pagination, PrimaryKey
from dispatch.organization.models import Organization, OrganizationRead


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
        "DispatchUserProject", cascade="all, delete-orphan", overlaps="users"
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
        return slugify(str(self.name))

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class Service(DispatchBase):
    id: PrimaryKey
    description: str | None = None
    external_id: str
    is_active: bool | None = None
    name: NameStr
    type: str | None = None


class ProjectBase(DispatchBase):
    id: PrimaryKey | None
    name: NameStr
    display_name: str | None = Field("")
    owner_email: EmailStr | None = None
    owner_conversation: str | None = None
    annual_employee_cost: int | None = 50000
    business_year_hours: int | None = 2080
    description: str | None = None
    default: bool = False
    color: str | None = None
    send_daily_reports: bool | None = Field(True)
    send_weekly_reports: bool | None = Field(False)
    weekly_report_notification_id: int | None = None
    enabled: bool | None = Field(True)
    storage_folder_one: str | None = None
    storage_folder_two: str | None = None
    storage_use_folder_one_as_primary: bool | None = Field(True)
    storage_use_title: bool | None = Field(False)
    allow_self_join: bool | None = Field(True)
    select_commander_visibility: bool | None = Field(True)
    report_incident_instructions: str | None = None
    report_incident_title_hint: str | None = None
    report_incident_description_hint: str | None = None
    snooze_extension_oncall_service: Service | None = None


class ProjectCreate(ProjectBase):
    organization: OrganizationRead


class ProjectUpdate(ProjectBase):
    send_daily_reports: bool | None = Field(True)
    send_weekly_reports: bool | None = Field(False)
    weekly_report_notification_id: int | None = None
    stable_priority_id: int | None
    snooze_extension_oncall_service_id: int | None


class ProjectRead(ProjectBase):
    id: PrimaryKey | None = None
    stable_priority: IncidentPriorityRead | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectPagination(Pagination):
    items: list[ProjectRead] = []
