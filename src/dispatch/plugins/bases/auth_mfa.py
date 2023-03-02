"""
.. module: dispatch.plugins.bases.mfa
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Sheldon <wshel@netflix.com>
"""
from dispatch.plugins.base import Plugin


class MultiFactorAuthenticationPlugin(Plugin):
    type = "auth-mfa"

    def send_push_notification(self, items, **kwargs):
        raise NotImplementedError
