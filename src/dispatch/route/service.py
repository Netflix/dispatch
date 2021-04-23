import logging
from typing import Any, List

from dispatch.search_filter import service as search_filter_service

from dispatch.incident.models import Incident
from dispatch.route.models import Recommendation, RecommendationMatch

log = logging.getLogger(__name__)


def get_resource_matches(
    *, db_session, incident: Incident, model: Any
) -> List[RecommendationMatch]:
    """Fetches all matching model entities for the given incident."""
    # get all entities with an associated filter
    resources = (
        db_session.query(model)
        .filter(model.project_id == incident.project_id)
        .filter(model.filters.any())
        .all()
    )

    matched_resources = []
    for resource in resources:
        for f in resource.filters:
            print(f.expression)
            match = search_filter_service.match(
                db_session=db_session,
                filter_spec=f.expression,
                class_instance=incident,
            )

            if match:
                matched_resources.append(RecommendationMatch(resource=resource))
                break

    return matched_resources


def get(*, db_session, incident: Incident, models: List[Any]) -> Recommendation:
    """Get routed resources."""

    matches = []
    for model in models:
        matches += get_resource_matches(db_session=db_session, incident=incident, model=model)

    recommendation = Recommendation(matches=matches)
    db_session.add(recommendation)
    db_session.commit()
    return recommendation
