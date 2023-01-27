from typing import Any, List, Optional
from pydantic import Field, SecretStr
from pydantic.json import pydantic_encoder

from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import TSVectorType, StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


from dispatch.database.core import Base
from dispatch.config import DISPATCH_ENCRYPTION_KEY
from dispatch.models import DispatchBase, ProjectMixin, PrimaryKey
from dispatch.plugins.base import plugins
from dispatch.project.models import ProjectRead


def show_secrets_encoder(obj):
    if type(obj) == SecretStr:
        return obj.get_secret_value()
    else:
        return pydantic_encoder(obj)


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

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        plugin = plugins.get(self.slug)
        return plugin.configuration_schema.schema()


class PluginInstance(Base, ProjectMixin):
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    _configuration = Column(
        StringEncryptedType(key=str(DISPATCH_ENCRYPTION_KEY), engine=AesEngine, padding="pkcs5")
    )
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")

    # this is some magic that allows us to use the plugin search vectors
    # against our plugin instances
    search_vector = association_proxy("plugin", "search_vector")

    @property
    def instance(self):
        """Fetches a plugin instance that matches this record."""
        plugin = plugins.get(self.plugin.slug)
        plugin.configuration = self.configuration
        plugin.project_id = self.project_id
        return plugin

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        plugin = plugins.get(self.plugin.slug)
        return plugin.configuration_schema.schema()

    @hybrid_property
    def configuration(self):
        """Property that correctly returns a plugins configuration object."""
        if self._configuration:
            plugin = plugins.get(self.plugin.slug)
            return plugin.configuration_schema.parse_raw(self._configuration)

    @configuration.setter
    def configuration(self, configuration):
        """Property that correctly sets a plugins configuration object."""
        if configuration:
            plugin = plugins.get(self.plugin.slug)
            config_object = plugin.configuration_schema.parse_obj(configuration)
            self._configuration = config_object.json(encoder=show_secrets_encoder)


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
    configuration_schema: Any
    description: Optional[str] = Field(None, nullable=True)


class PluginInstanceRead(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration: Optional[dict]
    configuration_schema: Any
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
