from datetime import datetime
from typing import List, Optional
from pydantic.fields import Field
from pydantic.networks import EmailStr
from pydantic.types import conint, constr

import validators
from pydantic import BaseModel, validator
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

# pydantic type that limits the range of primary keys
PrimaryKey = conint(gt=0, lt=2147483647)
NameStr = constr(regex=r"^[\w ]+$", strip_whitespace=True, min_length=3)
OrganizationSlug = constr(regex="^[a-z0-9]+(?:-[a-z0-9]+)*$")


# SQLAlchemy models...
class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):  # noqa
        return relationship("Project")


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class ContactMixin(TimeStampMixin):
    """Contact mixin"""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)


# Pydantic models...
class DispatchBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True


class ResourceBase(DispatchBase):
    resource_type: Optional[str] = Field(None, nullable=True)
    resource_id: Optional[str] = Field(None, nullable=True)
    weblink: Optional[str] = Field(None, nullable=True)

    @validator("weblink")
    def sanitize_weblink(cls, v):
        if v:
            if not validators.url(v):
                raise ValueError("Weblink must be a valid url.")
        return v


class ContactBase(DispatchBase):
    email: EmailStr
    name: Optional[str] = Field(None, nullable=True)
    is_active: Optional[bool] = True
    is_external: Optional[bool] = False
    company: Optional[str] = Field(None, nullable=True)
    contact_type: Optional[str] = Field(None, nullable=True)
    notes: Optional[str] = Field(None, nullable=True)
    owner: Optional[str] = Field(None, nullable=True)


class PluginOptionModel(DispatchBase):
    pass


# self referential models
class TermNested(DispatchBase):
    id: Optional[PrimaryKey]
    text: str
    # disabling this for now as recursive models break swagger api gen
    # definitions: Optional[List["DefinitionNested"]] = []


class DefinitionNested(DispatchBase):
    id: Optional[PrimaryKey]
    text: str
    terms: Optional[List["TermNested"]] = []


class ServiceNested(DispatchBase):
    pass


class IndividualNested(DispatchBase):
    pass


class TeamNested(DispatchBase):
    pass


class TermReadNested(DispatchBase):
    id: PrimaryKey
    text: str


class DefinitionReadNested(DispatchBase):
    id: PrimaryKey
    text: str


class ServiceReadNested(DispatchBase):
    name: Optional[str] = Field(None, nullable=True)
    external_id: Optional[str] = Field(None, nullable=True)
    is_active: Optional[bool] = False
    type: Optional[str] = Field(None, nullable=True)


class IndividualReadNested(ContactBase):
    id: Optional[PrimaryKey]
    title: Optional[str] = Field(None, nullable=True)
    external_id: Optional[str]
    weblink: Optional[str]
    title: Optional[str]


class TeamReadNested(ContactBase):
    pass
