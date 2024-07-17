"""Migrates the storage setting to the google drive plugin

Revision ID: d1dc160533c7
Revises: ceaf01079f4f
Create Date: 2021-10-27 14:03:01.385859

"""
import json
from alembic import op
from pydantic import SecretStr
from pydantic.json import pydantic_encoder
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy_utils import StringEncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from dispatch.config import DISPATCH_ENCRYPTION_KEY, Config

config = Config(".env")


# revision identifiers, used by Alembic.
revision = "d1dc160533c7"
down_revision = "ceaf01079f4f"
branch_labels = None
depends_on = None

Base = declarative_base()


def show_secrets_encoder(obj):
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    else:
        return pydantic_encoder(obj)


class Plugin(Base):
    __tablename__ = "plugin"
    __table_args__ = {"schema": "dispatch_core"}
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)


class PluginInstance(Base):
    __tablename__ = "plugin_instance"
    id = Column(Integer, primary_key=True)
    _configuration = Column(
        StringEncryptedType(key=str(DISPATCH_ENCRYPTION_KEY), engine=AesEngine, padding="pkcs5")
    )
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    instances = session.query(PluginInstance).filter(Plugin.slug == "google-drive-storage").all()

    for instance in instances:
        if instance._configuration:
            configuration_json = json.loads(instance._configuration)
            configuration_json["root_id"] = config("INCIDENT_STORAGE_FOLDER_ID")
            configuration_json["open_on_close"] = config(
                "INCIDENT_STORAGE_OPEN_ON_CLOSE", default=False
            )
            instance._configuration = json.dumps(configuration_json)

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    pass
