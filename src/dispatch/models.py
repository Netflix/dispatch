from datetime import datetime
from typing import List, Optional

import validators
from pydantic import BaseModel, validator
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


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
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    weblink: Optional[str] = None

    @validator("weblink")
    def sanitize_weblink(cls, v):
        if v:
            if not validators.url(v):
                raise ValueError("Weblink must be a valid url.")
        return v


class ContactBase(DispatchBase):
    email: str
    name: Optional[str] = None
    is_active: Optional[bool] = True
    is_external: Optional[bool] = False
    company: Optional[str] = None
    contact_type: Optional[str] = None
    notes: Optional[str] = None
    owner: Optional[str] = None


class PluginOptionModel(DispatchBase):
    pass


# self referential models
class TermNested(DispatchBase):
    id: Optional[int]
    text: str
    # disabling this for now as recursive models break swagger api gen
    # definitions: Optional[List["DefinitionNested"]] = []


class DefinitionNested(DispatchBase):
    id: Optional[int]
    text: str
    terms: Optional[List["TermNested"]] = []


class ServiceNested(DispatchBase):
    pass


class IndividualNested(DispatchBase):
    pass


class TeamNested(DispatchBase):
    pass


class TermReadNested(DispatchBase):
    id: int
    text: str


class DefinitionReadNested(DispatchBase):
    id: int
    text: str


class ServiceReadNested(DispatchBase):
    name: Optional[str] = None
    external_id: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


class IndividualReadNested(ContactBase):
    id: Optional[int]
    title: Optional[str] = None
    external_id: Optional[str]
    weblink: Optional[str]
    title: Optional[str]


class TeamReadNested(ContactBase):
    pass
