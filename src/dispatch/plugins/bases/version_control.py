"""
.. module: dispatch.plugins.bases.version_control
    :platform: Unix
    :copyright: (c) 2024 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

from dispatch.plugins.base import Plugin


class VesionControlPlugin(Plugin):
    type = "version-control"

    def get_repo(self, **kwargs):
        raise NotImplementedError

    def clone_repo(self, **kwargs):
        raise NotImplementedError

    def create_pr(self, **kwargs):
        raise NotImplementedError

    def close_pr(self, **kwargs):
        raise NotImplementedError
