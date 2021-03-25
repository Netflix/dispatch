from pydantic import validator

from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey

from dispatch.database.base import Base
from dispatch.messaging.strings import INCIDENT_STORAGE_DESCRIPTION
from dispatch.models import DispatchBase, ResourceMixin


class Storage(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))


# Pydantic models...
class StorageBase(DispatchBase):
    resource_id: Optional[str]
    resource_type: Optional[str]
    weblink: Optional[str]


class StorageCreate(StorageBase):
    pass


class StorageUpdate(StorageBase):
    pass


class StorageRead(StorageBase):
    description: Optional[str]

    @validator("description", pre=True, always=True)
    def set_description(cls, v):
        """Sets the description"""
        return INCIDENT_STORAGE_DESCRIPTION


class StorageNested(StorageBase):
    pass
