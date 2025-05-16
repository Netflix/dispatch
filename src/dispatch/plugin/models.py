import logging

from pydantic import SecretStr
from pydantic.json import pydantic_encoder

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType, StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from dispatch.config import DISPATCH_ENCRYPTION_KEY
from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin, Pagination, PrimaryKey, NameStr
from dispatch.plugins.base import plugins
from dispatch.project.models import ProjectRead
from typing import Any

logger = logging.getLogger(__name__)


def show_secrets_encoder(obj):
    if isinstance(obj, SecretStr):
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
        try:
            plugin = plugins.get(self.slug)
            if getattr(plugin, "configuration_schema", None) is not None:
                return plugin.configuration_schema.schema()
            return None
        except Exception as e:
            logger.warning(
                f"Error trying to load configuration_schema for plugin with slug {self.slug}: {e}"
            )
            return None


# SQLAlchemy Model
class PluginEvent(Base):
    __table_args__ = {"schema": "dispatch_core"}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, foreign_keys=[plugin_id])

    search_vector = Column(
        TSVectorType(
            "name",
            "slug",
            "description",
            weights={"name": "A", "slug": "B", "description": "C"},
        )
    )


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
        try:
            plugin = plugins.get(self.plugin.slug)
            plugin.configuration = self.configuration
            plugin.project_id = self.project_id
            return plugin
        except Exception as e:
            logger.warning(f"Error trying to load plugin with slug {self.slug}: {e}")
            return self.plugin

    @property
    def broken(self):
        try:
            plugins.get(self.plugin.slug)
            return False
        except Exception:
            return True

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        try:
            plugin = plugins.get(self.plugin.slug)
            if getattr(plugin, "configuration_schema", None) is not None:
                return plugin.configuration_schema.schema()
            return None
        except Exception as e:
            logger.warning(
                f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}"
            )
            return None

    @hybrid_property
    def configuration(self):
        """Property that correctly returns a plugins configuration object."""
        try:
            if self._configuration:
                plugin = plugins.get(self.plugin.slug)
                return plugin.configuration_schema.parse_raw(self._configuration)
        except Exception as e:
            logger.warning(
                f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}"
            )
            return None

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
    description: str | None = None


class PluginEventBase(DispatchBase):
    name: NameStr
    slug: str
    plugin: PluginRead
    description: str | None = None


class PluginEventRead(PluginEventBase):
    id: PrimaryKey


class PluginEventCreate(PluginEventBase):
    pass


class PluginEventPagination(Pagination):
    items: list[PluginEventRead] = []


class PluginInstanceRead(PluginBase):
    id: PrimaryKey
    enabled: bool | None
    configuration: dict | None
    configuration_schema: Any
    plugin: PluginRead
    project: ProjectRead | None
    broken: bool | None


class PluginInstanceReadMinimal(PluginBase):
    id: PrimaryKey
    enabled: bool | None
    configuration_schema: Any
    plugin: PluginRead
    project: ProjectRead | None
    broken: bool | None


class PluginInstanceCreate(PluginBase):
    enabled: bool | None = None
    configuration: dict | None = None
    plugin: PluginRead
    project: ProjectRead


class PluginInstanceUpdate(PluginBase):
    id: PrimaryKey = None
    enabled: bool | None
    configuration: dict | None


class KeyValue(DispatchBase):
    key: str
    value: str | list[str] | dict


class PluginMetadata(DispatchBase):
    slug: str
    metadata: list[KeyValue] = []


class PluginPagination(Pagination):
    items: list[PluginRead] = []


class PluginInstancePagination(Pagination):
    items: list[PluginInstanceReadMinimal] = []
