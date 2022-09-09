"""
.. module: dispatch.plugins.dispatch_aws.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_aws as aws_plugin
from dispatch.plugins.bases import SignalEnrichmentPlugin

from .config import AWSConfiguration

log = logging.getLogger(__name__)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class AWSSignalEnrichmentPlugin(SignalEnrichmentPlugin):
    title = "AWS Plugin - Signal enrichment"
    slug = "aws-signal-enrichment"
    description = "Uses AWS as a signal enrichment source."
    version = aws_plugin.__version__

    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = AWSConfiguration

    def enrich(
        self, name: str, description: str = None, title: str = None, participants: List[str] = []
    ):
        """Enriches an event."""
        return {}
