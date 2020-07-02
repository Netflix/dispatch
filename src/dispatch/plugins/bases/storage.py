"""
.. module: dispatch.plugins.bases.storage
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.models import PluginOptionModel
from dispatch.plugins.base import Plugin


class StoragePlugin(Plugin):
    type = "storage"
    _schema = PluginOptionModel

    def get(self, **kwargs):
        raise NotImplementedError

    def create(self, items, **kwargs):
        raise NotImplementedError

    def update(self, items, **kwargs):
        raise NotImplementedError

    def delete(self, items, **kwargs):
        raise NotImplementedError

    def list(self, **kwargs):
        raise NotImplementedError

    def add_participant(self, items, **kwargs):
        raise NotImplementedError

    def remove_participant(self, items, **kwargs):
        raise NotImplementedError

    def open(self, **kwargs):
        raise NotImplementedError

    def add_file(self, **kwargs):
        raise NotImplementedError

    def delete_file(self, **kwargs):
        raise NotImplementedError

    def move_file(self, **kwargs):
        raise NotImplementedError

    def list_files(self, **kwargs):
        raise NotImplementedError
