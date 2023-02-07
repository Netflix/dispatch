import json
import logging
from typing import Any, List

from dispatch.database.core import Base
from dispatch.route.models import Recommendation, RecommendationMatch
from dispatch.search_filter import service as search_filter_service

log = logging.getLogger(__name__)


def get_resource_matches(
    *, db_session, project_id: int, class_instance: Base, model: Any
) -> List[RecommendationMatch]:
    """Fetches all matching model entities for the given class instance."""
    # get all entities with an associated filter
    model_cls, model_state = model
    resources = (
        db_session.query(model_cls)
        .filter(model_cls.project_id == project_id)
        .filter(model_cls.filters.any())
        .all()
    )

    matched_resources = []
    for resource in resources:
        for f in resource.filters:
            match = search_filter_service.match(
                db_session=db_session,
                subject=f.subject,
                filter_spec=f.expression,
                class_instance=class_instance,
            )

            if match:
                matched_resources.append(
                    RecommendationMatch(
                        resource_state=json.loads(model_state(**resource.__dict__).json()),
                        resource_type=model_cls.__name__,
                    )
                )
                break

    return matched_resources


def get(*, db_session, project_id: int, class_instance: Base, models: List[Any]) -> Recommendation:
    """Get routed resources."""

    matches = []
    for model in models:
        matches += get_resource_matches(
            db_session=db_session, project_id=project_id, class_instance=class_instance, model=model
        )

    recommendation = Recommendation(matches=matches)
    db_session.add(recommendation)
    db_session.commit()
    return recommendation
