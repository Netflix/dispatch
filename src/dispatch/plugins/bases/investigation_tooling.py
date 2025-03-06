"""
.. module: dispatch.plugins.bases.investigation_tooling
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""

from dispatch.case.models import Case
from dispatch.plugins.base import Plugin


class InvestigationToolingPlugin(Plugin):
    """Investigation tooling base plugin class."""

    type = "investigation-tooling"

    def create_investigation(self, case: Case, **kwargs):
        """Creates a new investigation.

        Args:
            case: Case object
            kwargs: Optional kwargs.

        Returns:
            Additional context.
        """
        raise NotImplementedError
