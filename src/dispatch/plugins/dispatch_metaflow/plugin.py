"""
.. module: dispatch.plugins.dispatch_metaflow.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.plugins.bases import ExternalFlowPlugin
from dispatch.plugins.dispatch_metaflow import plugin as metaflow_plugin
from metaflow import Metaflow, Meson, MesonDuplicateSignal, namespace

from .config import METAFLOW_NAMESPACE

log = logging.getLogger(__name__)


class MetaflowExternalFlowPlugin(ExternalFlowPlugin):
    title = "Metaflow - External flows"
    slug = "metaflow-external-flow"
    description = "Metaflow external flow runner."
    version = metaflow_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def list(self, **kwargs):
        namespace(METAFLOW_NAMESPACE)
        return Metaflow().flows

    def run(self, name, **kwargs):
        try:
            Meson.send_signal(name, kwargs)
        except MesonDuplicateSignal:
            log.debug(f"Triggering signal already exists. Name: {name} Kwargs: {kwargs}")
