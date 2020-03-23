"""
.. module: dispatch.plugins.bases.application
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.models import PluginOptionModel
from dispatch.plugins.base import Plugin
from starlette.requests import Request


class AuthenticationProviderPlugin(Plugin):
    type = "auth-provider"
    _schema = PluginOptionModel

    def get_current_user(self, request: Request, **kwargs):
        raise NotImplementedError
