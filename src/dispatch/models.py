from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event, ForeignKey
from sqlalchemy.ext.declarative import declared_attr


# SQLAlchemy models...
class TimeStampMixin(object):
    """ Timestamping mixin"""

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
    """ Contact mixin"""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String, unique=True)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)

    @declared_attr
    def incident_id(cls):  # noqa
        return Column(Integer, ForeignKey("incident.id"))


# Pydantic models...
class DispatchBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True


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
    weblink: Optional[str]
    title: Optional[str]


class TeamReadNested(ContactBase):
    pass


class PolicyReadNested(DispatchBase):
    pass
