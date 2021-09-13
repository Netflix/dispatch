from typing import List, Optional
from pydantic import Field

from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy_utils import TSVectorType, JSONType
from dispatch import plugin

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin, PrimaryKey
from dispatch.plugins.base import plugins
from dispatch.project.models import ProjectRead


class Plugin(Base):
    __table_args__ = {"schema": "dispatch_core"}
    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    version = Column(String)
    author = Column(String)
    author_url = Column(String)
    type = Column(String)
    multiple = Column(Boolean)

    search_vector = Column(
        TSVectorType(
            "title",
            "slug",
            "type",
            "description",
            weights={"title": "A", "slug": "B", "type": "C", "description": "C"},
        )
    )


class PluginInstance(Base, ProjectMixin):
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    configuration = Column(JSONType)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")

    # this is some magic that allows us to use the plugin search vectors
    # against our plugin instances
    search_vector = association_proxy("plugin", "search_vector")

    @property
    def instance(self):
        """Fetches a plugin instance that matches this record."""
        plugin_instance = plugins.get(self.plugin.slug)
        plugin_instance.configuration(plugin_instance._schema(**self.configuration))
        return plugin


# Pydantic models...
class PluginBase(DispatchBase):
    pass


class PluginRead(PluginBase):
    id: PrimaryKey
    title: str
    slug: str
    author: str
    author_url: str
    type: str
    multiple: bool
    description: Optional[str] = Field(None, nullable=True)


class PluginInstanceRead(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration: Optional[dict]
    plugin: PluginRead
    project: Optional[ProjectRead]


class PluginInstanceCreate(PluginBase):
    enabled: Optional[bool]
    configuration: Optional[dict]
    plugin: PluginRead
    project: ProjectRead


class PluginInstanceUpdate(PluginBase):
    id: PrimaryKey = None
    enabled: Optional[bool]
    configuration: Optional[dict]


class KeyValue(DispatchBase):
    key: str
    value: str


class PluginMetadata(DispatchBase):
    slug: str
    metadata: List[KeyValue] = []


class PluginPagination(DispatchBase):
    total: int
    items: List[PluginRead] = []


class PluginInstancePagination(DispatchBase):
    total: int
    items: List[PluginInstanceRead] = []
