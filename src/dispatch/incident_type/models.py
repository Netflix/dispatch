from typing import List, Optional
from pydantic import validator

from sqlalchemy import event, Column, Boolean, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.enums import Visibility
from dispatch.models import DispatchBase
from dispatch.plugin.models import PluginMetadata


class IncidentType(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    slug = Column(String)
    description = Column(String)
    exclude_from_metrics = Column(Boolean, default=False)
    default = Column(Boolean, default=False)
    visibility = Column(String, default=Visibility.open)
    plugin_metadata = Column(JSON, default=[])

    template_document_id = Column(Integer, ForeignKey("document.id"))
    template_document = relationship("Document")

    commander_service_id = Column(Integer, ForeignKey("service.id"))
    commander_service = relationship("Service", foreign_keys=[commander_service_id])

    liaison_service_id = Column(Integer, ForeignKey("service.id"))
    liaison_service = relationship("Service", foreign_keys=[liaison_service_id])

    search_vector = Column(TSVectorType("name", "description"))

    @hybrid_method
    def get_meta(self, slug):
        if not self.plugin_metadata:
            return

        for m in self.plugin_metadata:
            if m["slug"] == slug:
                return m


@event.listens_for(IncidentType.default, "set")
def _revoke_other_default(target, value, oldvalue, initiator):
    """Removes the previous default when a new one is set."""
    session = object_session(target)
    if session is None:
        return

    if value:
        previous_default = (
            session.query(IncidentType).filter(IncidentType.default == True).one_or_none()  # noqa
        )

        if previous_default:
            previous_default.default = False
            session.commit()


class Document(DispatchBase):
    id: int
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str


class Service(DispatchBase):
    id: int
    name: Optional[str] = None
    external_id: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


# Pydantic models...
class IncidentTypeBase(DispatchBase):
    name: str
    description: Optional[str]


class IncidentTypeCreate(IncidentTypeBase):
    template_document: Optional[Document]
    commander_service: Optional[Service]
    liaison_service: Optional[Service]
    plugin_metadata: List[PluginMetadata] = []
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class IncidentTypeUpdate(IncidentTypeBase):
    id: int
    visibility: Optional[Visibility]
    template_document: Optional[Document]
    commander_service: Optional[Service]
    liaison_service: Optional[Service]
    plugin_metadata: List[PluginMetadata] = []
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class IncidentTypeRead(IncidentTypeBase):
    id: int
    visibility: Optional[Visibility]
    template_document: Optional[Document]
    commander_service: Optional[Service]
    liaison_service: Optional[Service]
    plugin_metadata: List[PluginMetadata] = []
    exclude_from_metrics: Optional[bool] = False
    default: Optional[bool] = False

    @validator("plugin_metadata", pre=True)
    def replace_none_with_empty_list(cls, value):
        return [] if value is None else value


class IncidentTypeNested(IncidentTypeBase):
    id: int


class IncidentTypePagination(DispatchBase):
    total: int
    items: List[IncidentTypeRead] = []
