"""
.. module: dispatch.tag.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.incident import service as incident_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import TagCreate
from dispatch.tag.recommender import build_model

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="tag-sync")
@background_task
def sync_tags(db_session=None):
    """Syncs tags from external sources."""
    for p in plugins.all(plugin_type="tag"):
        log.debug(f"Getting tags via: {p.slug}")
        for t in p.get():
            log.debug(f"Adding Tag. Tag: {t}")
            tag_service.get_or_create(db_session=db_session, tag_in=TagCreate(**t))


@scheduler.add(every(1).hour, name="tag-model-builder")
@background_task
def build_tag_models(db_session=None):
    """Builds the intensive tag recommandation models."""
    # incident model
    incidents = incident_service.get_all(db_session=db_session).all()
    log.debug("Starting to build the incident/tag model...")
    build_model(incidents, "incident")
    log.debug("Successfully built the incident/tag model.")
